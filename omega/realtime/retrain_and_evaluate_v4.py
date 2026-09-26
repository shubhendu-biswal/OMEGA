import os
import sys
import json
import time
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score
)

sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
MODELS_DIR = os.path.join(CURRENT_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

TARGET_CLASSES = [
    "math",
    "gk",
    "agriculture",
    "crop_recommendation",
    "fertilizer_recommendation",
    "conversation",
    "out_of_scope",
    "realtime"
]

def load_data():
    train_path = os.path.join(DATA_DIR, "intent_train_v4.json")
    test_path = os.path.join(DATA_DIR, "intent_held_out_test_v3.json")
    hw_path = os.path.join(DATA_DIR, "handwritten_test_100.json")
    mandi_path = os.path.join(DATA_DIR, "mandi_handcrafted_150.json")
    
    with open(train_path, "r", encoding="utf-8") as f:
        train_data = json.load(f)
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    with open(hw_path, "r", encoding="utf-8") as f:
        hw_data = json.load(f)
    with open(mandi_path, "r", encoding="utf-8") as f:
        mandi_data = json.load(f)
        
    return train_data, test_data, hw_data, mandi_data

def train_and_evaluate():
    print("=" * 75)
    print("  OMEGA Stage 1 (Hardened): Retraining & Final Comprehensive Evaluation")
    print("=" * 75)
    
    train_data, test_data, hw_data, mandi_data = load_data()
    X_train = [r["text"] for r in train_data]
    y_train = [r["intent"] for r in train_data]
    
    X_test = [r["text"] for r in test_data]
    y_test = [r["intent"] for r in test_data]
    
    X_hw = [r["text"] for r in hw_data]
    y_hw = [r["intent"] for r in hw_data]
    
    X_mandi = [r["text"] for r in mandi_data]
    y_mandi = [r["intent"] for r in mandi_data]
    
    print(f"Dataset summary:")
    print(f"  - Augmented Training samples (v4): {len(X_train):,}")
    print(f"  - Synthetic Held-out test samples:  {len(X_test):,}")
    print(f"  - Independent Hand-written samples: {len(X_hw):,}")
    print(f"  - Mandi evaluation benchmark:       {len(X_mandi):,}")
    
    # 1. Feature Extraction: Dual Word + Character n-grams
    print("\n[1/4] Constructing Feature Extraction Pipeline...")
    word_vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_features=32000,
        token_pattern=r'(?u)\b\w+\b'
    )
    
    char_vectorizer = TfidfVectorizer(
        ngram_range=(2, 5),
        analyzer='char',
        sublinear_tf=True,
        min_df=3,
        max_features=48000
    )
    
    features = FeatureUnion([
        ('word', word_vectorizer),
        ('char', char_vectorizer)
    ])
    
    base_clf = LinearSVC(C=1.5, class_weight='balanced', random_state=42, max_iter=3000)
    calibrated_clf = CalibratedClassifierCV(estimator=base_clf, method='sigmoid', cv=3)
    
    pipeline = Pipeline([
        ('features', features),
        ('classifier', calibrated_clf)
    ])
    
    # 2. Train Model
    print("\n[2/4] Training Model on Augmented Dataset (v4)...")
    start_time = time.time()
    pipeline.fit(X_train, y_train)
    train_duration = time.time() - start_time
    print(f"  Model trained in {train_duration:.2f} seconds.")
    
    classes = list(pipeline.classes_)
    
    # 3. Evaluate on Synthetic Held-Out Test Set
    print("\n[3/4] Evaluating on SYNTHETIC HELD-OUT Test Split (5,877 Samples)...")
    y_test_pred = pipeline.predict(X_test)
    y_test_probs = pipeline.predict_proba(X_test)
    
    test_acc = accuracy_score(y_test, y_test_pred)
    macro_f1 = f1_score(y_test, y_test_pred, average='macro')
    weighted_f1 = f1_score(y_test, y_test_pred, average='weighted')
    
    print(f"\nSYNTHETIC HELD-OUT EVALUATION METRICS:")
    print(f"  - Overall Accuracy:  {test_acc * 100:.2f}% ({int(test_acc * len(y_test))}/{len(y_test)})")
    print(f"  - Macro-F1 Score:    {macro_f1:.4f}")
    print(f"  - Weighted-F1 Score: {weighted_f1:.4f}")
    
    report_dict_test = classification_report(y_test, y_test_pred, labels=classes, target_names=classes, output_dict=True)
    report_str_test = classification_report(y_test, y_test_pred, labels=classes, target_names=classes, digits=4)
    print("\nDetailed Per-Class Classification Report (Synthetic Held-Out Test):")
    print(report_str_test)
    
    cm_test = confusion_matrix(y_test, y_test_pred, labels=classes)
    print("\nFull Confusion Matrix (Synthetic Test):")
    header = f"{'':<26}" + "".join([f"{c[:10]:>12}" for c in classes])
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(cm_test):
        row_str = "".join([f"{val:>12}" for val in row])
        print(f"{classes[idx]:<26}{row_str}")

    realtime_recall_test = report_dict_test["realtime"]["recall"]
    realtime_prec_test = report_dict_test["realtime"]["precision"]
    realtime_f1_test = report_dict_test["realtime"]["f1-score"]

    # GK misroute to realtime rate
    gk_total = 0
    gk_misrouted_to_realtime = 0
    for true_y, pred_y in zip(y_test, y_test_pred):
        if true_y == "gk":
            gk_total += 1
            if pred_y == "realtime":
                gk_misrouted_to_realtime += 1
    gk_misroute_rate = (gk_misrouted_to_realtime / gk_total) if gk_total > 0 else 0.0

    # 4. Evaluate on Independent Hand-Written Test Set
    print("\n[4/4] Evaluating on INDEPENDENT HAND-WRITTEN Test Set (101 Samples)...")
    y_hw_pred = pipeline.predict(X_hw)
    y_hw_probs = pipeline.predict_proba(X_hw)
    
    hw_acc = accuracy_score(y_hw, y_hw_pred) * 100
    hw_macro_f1 = f1_score(y_hw, y_hw_pred, average='macro')
    
    report_dict_hw = classification_report(y_hw, y_hw_pred, labels=classes, target_names=classes, output_dict=True)
    report_str_hw = classification_report(y_hw, y_hw_pred, labels=classes, target_names=classes, digits=4)
    print(f"\nINDEPENDENT HAND-WRITTEN TEST EVALUATION METRICS:")
    print(f"  - Overall Accuracy:  {hw_acc:.2f}% ({int(accuracy_score(y_hw, y_hw_pred) * len(y_hw))}/{len(y_hw)})")
    print(f"  - Macro-F1 Score:    {hw_macro_f1:.4f}")
    print("\nDetailed Per-Class Classification Report (Hand-Written Test):")
    print(report_str_hw)

    cm_hw = confusion_matrix(y_hw, y_hw_pred, labels=classes)
    print("\nFull Confusion Matrix (Hand-Written Test):")
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(cm_hw):
        row_str = "".join([f"{val:>12}" for val in row])
        print(f"{classes[idx]:<26}{row_str}")

    # Check for any class below 90% recall on handwritten set
    classes_below_90_recall = []
    print("\nPer-Class Recall Verification on Hand-Written Test Set (Requirement: >= 90% for ALL classes):")
    for c in classes:
        rec = report_dict_hw[c]["recall"] * 100
        prec = report_dict_hw[c]["precision"] * 100
        f1 = report_dict_hw[c]["f1-score"] * 100
        sup = report_dict_hw[c]["support"]
        passed = rec >= 90.0
        if not passed:
            classes_below_90_recall.append((c, rec))
        print(f"  * {c:<26}: Recall = {rec:>6.2f}% | Precision = {prec:>6.2f}% | F1 = {f1:>6.2f}% (Support: {sup}) -> {'[PASS]' if passed else '[FAIL]'}")

    # 5. Evaluate Mandi Price Accuracy & Confidence (Before vs After)
    preds_mandi = pipeline.predict(X_mandi)
    probs_mandi = pipeline.predict_proba(X_mandi)
    correct_mandi = sum(1 for p, y in zip(preds_mandi, y_mandi) if p == y)
    mandi_acc_after = (correct_mandi / len(y_mandi)) * 100
    
    confidences_mandi_after = []
    for i, p in enumerate(preds_mandi):
        pred_idx = classes.index(p)
        confidences_mandi_after.append(float(probs_mandi[i][pred_idx]))
    mandi_avg_conf_after = np.mean(confidences_mandi_after) * 100

    print("\n" + "=" * 75)
    print("  MANDI / MARKET PRICE ACCURACY & CONFIDENCE (BEFORE vs AFTER)")
    print("=" * 75)
    print(f"  * Before Fixes: Accuracy = 72.00% (108/150) | Average Confidence = 79.57%")
    print(f"  * After Fixes:  Accuracy = {mandi_acc_after:.2f}% ({correct_mandi}/{len(y_mandi)}) | Average Confidence = {mandi_avg_conf_after:.2f}%")
    print(f"  * Absolute Accuracy Gain:   +{mandi_acc_after - 72.00:.2f}%")
    print(f"  * Absolute Confidence Gain: +{mandi_avg_conf_after - 79.57:.2f}%")
    pass_mandi = mandi_acc_after >= 90.0
    print(f"  * Mandi Criterion (Accuracy >= 90%): {'[PASS]' if pass_mandi else '[FAIL]'}")

    print("\n" + "=" * 75)
    print("  STAGE 1 FINAL PASS CRITERIA VERIFICATION")
    print("=" * 75)
    pass_hw_all_90 = len(classes_below_90_recall) == 0
    pass_gk = gk_misroute_rate < 0.05
    pass_realtime_recall = realtime_recall_test > 0.90
    
    print(f"  1. Realtime Recall on Synthetic Held-Out: {realtime_recall_test*100:.2f}% (Threshold: > 90%) -> {'[PASS]' if pass_realtime_recall else '[FAIL]'}")
    print(f"  2. Static GK Misrouted to Realtime:       {gk_misroute_rate*100:.2f}% (Threshold: < 5%) -> {'[PASS]' if pass_gk else '[FAIL]'}")
    print(f"  3. Mandi-Price Specific Accuracy:         {mandi_acc_after:.2f}% (Threshold: > 90%) -> {'[PASS]' if pass_mandi else '[FAIL]'}")
    print(f"  4. No Class Below 90% Recall on HW Set:   {len(classes_below_90_recall)} failing classes -> {'[PASS]' if pass_hw_all_90 else '[FAIL]'}")
    
    overall_stage1_ready = pass_realtime_recall and pass_gk and pass_mandi and pass_hw_all_90
    print(f"\n  OVERALL READINESS FOR STAGE 2: {'[APPROVED FOR STAGE 2]' if overall_stage1_ready else '[NEEDS REFINEMENT]'}")
    print("=" * 75)

    # 6. Save Model Artifacts
    model_file = os.path.join(MODELS_DIR, "realtime_intent_model.pkl")
    metadata_file = os.path.join(MODELS_DIR, "realtime_intent_metadata.json")
    
    joblib.dump(pipeline, model_file)
    print(f"\nSaved updated trained pipeline to: {model_file}")
    
    metadata = {
        "model_type": "FeatureUnion(Word_Char_TFIDF) + CalibratedClassifierCV(LinearSVC)",
        "classes": classes,
        "num_training_samples": len(X_train),
        "synthetic_metrics": {
            "num_samples": len(X_test),
            "accuracy": round(test_acc, 4),
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "realtime_precision": round(realtime_prec_test, 4),
            "realtime_recall": round(realtime_recall_test, 4),
            "realtime_f1": round(realtime_f1_test, 4),
            "static_gk_misroute_to_realtime_rate": round(gk_misroute_rate, 4)
        },
        "handwritten_metrics": {
            "num_samples": len(X_hw),
            "accuracy": round(hw_acc / 100.0, 4),
            "macro_f1": round(hw_macro_f1, 4),
            "classes_below_90_recall": classes_below_90_recall
        },
        "mandi_benchmark": {
            "before_accuracy": 72.00,
            "before_confidence": 79.57,
            "after_accuracy": round(mandi_acc_after, 2),
            "after_confidence": round(mandi_avg_conf_after, 2)
        },
        "pass_status": {
            "mandi_above_90": bool(pass_mandi),
            "no_hw_class_below_90_recall": bool(pass_hw_all_90),
            "realtime_recall_above_90": bool(pass_realtime_recall),
            "gk_misroute_below_5": bool(pass_gk),
            "overall_approved": bool(overall_stage1_ready)
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to: {metadata_file}")
    
    # Non-destructive copy in ml_service assets
    v2_assets_dir = os.path.join(CURRENT_DIR, "..", "..", "ml_service", "assets", "v2", "intent")
    try:
        os.makedirs(v2_assets_dir, exist_ok=True)
        joblib.dump(pipeline, os.path.join(v2_assets_dir, "intent_model_v3_realtime.pkl"))
        with open(os.path.join(v2_assets_dir, "intent_metadata_v3_realtime.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved non-destructive copy to: {v2_assets_dir}/intent_model_v3_realtime.pkl")
    except Exception as e:
        print(f"Note on v2 sync: {e}")

    # Return results dictionary
    return {
        "test_acc": test_acc,
        "macro_f1": macro_f1,
        "report_dict_test": report_dict_test,
        "cm_test": cm_test.tolist(),
        "hw_acc": hw_acc,
        "hw_macro_f1": hw_macro_f1,
        "report_dict_hw": report_dict_hw,
        "cm_hw": cm_hw.tolist(),
        "mandi_acc_after": mandi_acc_after,
        "mandi_avg_conf_after": mandi_avg_conf_after,
        "classes": classes,
        "classes_below_90_recall": classes_below_90_recall,
        "overall_stage1_ready": overall_stage1_ready
    }

if __name__ == "__main__":
    train_and_evaluate()
