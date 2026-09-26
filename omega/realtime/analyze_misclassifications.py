import os
import json
import joblib
import numpy as np
from collections import defaultdict, Counter

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "models", "realtime_intent_model.pkl")
TEST_DATA_PATH = os.path.join(CURRENT_DIR, "data", "intent_held_out_test_v3.json")

def main():
    model = joblib.load(MODEL_PATH)
    with open(TEST_DATA_PATH, "r", encoding="utf-8") as f:
        test_data = json.load(f)
        
    X_test = [r["text"] for r in test_data]
    y_test = [r["intent"] for r in test_data]
    
    classes = list(model.classes_)
    y_pred = model.predict(X_test)
    y_probs = model.predict_proba(X_test)
    
    print("=" * 80)
    print("1. FULL CONFUSION MATRIX (Rows: True, Cols: Pred)")
    print("=" * 80)
    
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, y_pred, labels=classes)
    
    header = f"{'':<26}" + "".join([f"{c[:10]:>12}" for c in classes])
    print(header)
    print("-" * len(header))
    for idx, row in enumerate(cm):
        row_str = "".join([f"{val:>12}" for val in row])
        print(f"{classes[idx]:<26}{row_str}")
        
    # Misclassification tracking
    misclassified_pairs = defaultdict(list)
    realtime_misclassifications = []
    
    for i, (text, true_lbl, pred_lbl) in enumerate(zip(X_test, y_test, y_pred)):
        if true_lbl != pred_lbl:
            prob = float(np.max(y_probs[i]))
            pred_class_prob = float(y_probs[i][classes.index(pred_lbl)])
            true_class_prob = float(y_probs[i][classes.index(true_lbl)])
            
            entry = {
                "text": text,
                "true": true_lbl,
                "pred": pred_lbl,
                "conf": round(pred_class_prob, 4),
                "true_conf": round(true_class_prob, 4)
            }
            misclassified_pairs[(true_lbl, pred_lbl)].append(entry)
            
            if true_lbl == "realtime":
                realtime_misclassifications.append(entry)
                
    print("\n" + "=" * 80)
    print(f"2. ALL REALTIME MISCLASSIFICATIONS ({len(realtime_misclassifications)} samples)")
    print("=" * 80)
    for idx, item in enumerate(realtime_misclassifications, 1):
        print(f"{idx:2d}. True: {item['true']} -> Pred: {item['pred']} (Conf: {item['conf']*100:.2f}%, Realtime Conf: {item['true_conf']*100:.2f}%)")
        print(f"    Text: \"{item['text']}\"")
        
    print("\n" + "=" * 80)
    print("3. TOP MISCLASSIFICATION PAIRS FOR AGRICULTURE, MATH, AND REALTIME")
    print("=" * 80)
    
    for target_class in ["agriculture", "math", "realtime"]:
        print(f"\n--- Analysis for Class: [{target_class}] ---")
        # Pairs where target_class is true_lbl
        pairs_for_class = [(k, v) for k, v in misclassified_pairs.items() if k[0] == target_class]
        pairs_for_class.sort(key=lambda x: len(x[1]), reverse=True)
        
        top3 = pairs_for_class[:3]
        for (true_c, pred_c), items in top3:
            print(f"\nPair: True [{true_c}] -> Predicted [{pred_c}] (Count: {len(items)})")
            print("5 Representative Examples:")
            for ex in items[:5]:
                print(f"  * \"{ex['text']}\" (Pred Conf: {ex['conf']*100:.2f}%, True Conf: {ex['true_conf']*100:.2f}%)")

    # Save details to json for reporting
    out_file = os.path.join(CURRENT_DIR, "data", "misclassifications_audit.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "confusion_matrix": cm.tolist(),
            "classes": classes,
            "realtime_misclassified": realtime_misclassifications,
            "top_pairs": {f"{k[0]}->{k[1]}": v for k, v in misclassified_pairs.items()}
        }, f, indent=2, ensure_ascii=False)
    print(f"\nSaved misclassification audit to: {out_file}")

if __name__ == "__main__":
    main()
