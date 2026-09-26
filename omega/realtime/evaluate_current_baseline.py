import os
import sys
import json
import joblib
import numpy as np
from collections import defaultdict, Counter
from sklearn.metrics import classification_report, accuracy_score, f1_score

sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "models", "realtime_intent_model.pkl")
MANDI_PATH = os.path.join(CURRENT_DIR, "data", "mandi_handcrafted_150.json")
HANDWRITTEN_PATH = os.path.join(CURRENT_DIR, "data", "handwritten_test_100.json")

def main():
    model = joblib.load(MODEL_PATH)
    classes = list(model.classes_)
    
    print("=" * 75)
    print("  CURRENT MODEL BASELINE EVALUATION (BEFORE RETRAINING)")
    print("=" * 75)
    
    # 1. Mandi Price Specific Evaluation (150 samples)
    with open(MANDI_PATH, "r", encoding="utf-8") as f:
        mandi_data = json.load(f)
    X_mandi = [r["text"] for r in mandi_data]
    y_mandi = [r["intent"] for r in mandi_data]
    
    preds_mandi = model.predict(X_mandi)
    probs_mandi = model.predict_proba(X_mandi)
    
    correct_mandi = sum(1 for p, y in zip(preds_mandi, y_mandi) if p == y)
    acc_mandi = (correct_mandi / len(y_mandi)) * 100
    
    # Extract confidence for the predicted class and specifically for realtime class
    confidences_mandi = []
    realtime_idx = classes.index("realtime")
    for i, p in enumerate(preds_mandi):
        pred_idx = classes.index(p)
        confidences_mandi.append(float(probs_mandi[i][pred_idx]))
        
    avg_conf_mandi = (np.mean(confidences_mandi)) * 100
    
    print(f"\n1. MANDI / MARKET PRICE SPECIFIC ACCURACY (150 Handcrafted Samples):")
    print(f"  - Accuracy:           {acc_mandi:.2f}% ({correct_mandi}/{len(y_mandi)})")
    print(f"  - Average Confidence: {avg_conf_mandi:.2f}%")
    
    # Misclassified mandi breakdown
    mandi_misclassified = []
    for text, y, p, conf in zip(X_mandi, y_mandi, preds_mandi, confidences_mandi):
        if y != p:
            mandi_misclassified.append((text, p, conf))
    print(f"  - Misclassified count: {len(mandi_misclassified)}")
    if mandi_misclassified:
        print("  - Misclassified samples:")
        for t, p, c in mandi_misclassified[:8]:
            print(f"    * \"{t}\" -> Predicted as [{p}] (Conf: {c*100:.2f}%)")

    # 2. Independent Hand-Written Test Set Evaluation (101 samples)
    with open(HANDWRITTEN_PATH, "r", encoding="utf-8") as f:
        hw_data = json.load(f)
    X_hw = [r["text"] for r in hw_data]
    y_hw = [r["intent"] for r in hw_data]
    
    preds_hw = model.predict(X_hw)
    probs_hw = model.predict_proba(X_hw)
    
    acc_hw = accuracy_score(y_hw, preds_hw) * 100
    macro_f1_hw = f1_score(y_hw, preds_hw, average="macro")
    
    print(f"\n2. INDEPENDENT HAND-WRITTEN TEST SET EVALUATION ({len(y_hw)} Samples):")
    print(f"  - Overall Accuracy:   {acc_hw:.2f}%")
    print(f"  - Macro-F1 Score:     {macro_f1_hw:.4f}")
    
    # Synthetic Held-Out Baseline Scores for comparison:
    # From Stage 1 log:
    synthetic_recalls = {
        "agriculture": 97.86,
        "conversation": 99.46,
        "crop_recommendation": 98.26,
        "fertilizer_recommendation": 99.69,
        "gk": 99.91,
        "math": 99.89,
        "out_of_scope": 96.05,
        "realtime": 95.52
    }
    
    hw_report = classification_report(y_hw, preds_hw, labels=classes, target_names=classes, output_dict=True)
    print(f"\nPer-Class Accuracy / Recall on Hand-Written Set vs Synthetic Held-Out:")
    print(f"{'Class':<26}{'HW Support':<12}{'HW Recall':<14}{'Synth Recall':<15}{'Drop (pts)':<12}{'Flagged?'}")
    print("-" * 88)
    
    flagged_classes = []
    for c in classes:
        support = hw_report[c]["support"]
        hw_rec = hw_report[c]["recall"] * 100
        synth_rec = synthetic_recalls.get(c, 0.0)
        drop = synth_rec - hw_rec
        flagged = drop > 10.0
        if flagged:
            flagged_classes.append((c, drop))
        flag_str = "[FLAGGED >10pt DROP]" if flagged else "[OK]"
        print(f"{c:<26}{support:<12}{hw_rec:>6.2f}%{synth_rec:>14.2f}%{drop:>10.2f}%    {flag_str}")
        
    print(f"\nClasses Flagged for > 10 Point Drop: {flagged_classes}")
    
    # Save baseline results
    out_file = os.path.join(CURRENT_DIR, "data", "current_baseline_metrics.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "mandi_accuracy": acc_mandi,
            "mandi_avg_confidence": avg_conf_mandi,
            "mandi_misclassified_count": len(mandi_misclassified),
            "mandi_misclassified": mandi_misclassified,
            "handwritten_accuracy": acc_hw,
            "handwritten_macro_f1": macro_f1_hw,
            "handwritten_report": hw_report,
            "flagged_classes": flagged_classes
        }, f, indent=2)
    print(f"\nSaved baseline evaluation results to: {out_file}")

if __name__ == "__main__":
    main()
