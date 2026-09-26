import os
import sys
import json
import joblib
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")
MODELS_DIR = os.path.join(CURRENT_DIR, "models")

model_path = os.path.join(MODELS_DIR, "realtime_intent_model.pkl")
test_path = os.path.join(DATA_DIR, "fresh_mandi_test_150.json")
train_path = os.path.join(DATA_DIR, "intent_train_v4.json")

print("=" * 75)
print("  EVALUATION OF CURRENT RETRAINED MODEL (v4) ON FRESH UNTOUCHED TEST SET")
print("=" * 75)

# 1. Overlap Check
with open(train_path, "r", encoding="utf-8") as f:
    train_data = json.load(f)
train_texts = set(r["text"].strip().lower() for r in train_data)

with open(test_path, "r", encoding="utf-8") as f:
    test_data = json.load(f)

overlaps = [r["text"] for r in test_data if r["text"].strip().lower() in train_texts]
print(f"Overlap check with training data (intent_train_v4.json):")
print(f"  Total test samples: {len(test_data)}")
print(f"  Exact string matches in training data: {len(overlaps)}")
assert len(overlaps) == 0, f"Detected {len(overlaps)} overlaps!"

# 2. Model Inference
print(f"\nLoading model from: {model_path}")
model = joblib.load(model_path)

X = [r["text"] for r in test_data]
y_true = [r["intent"] for r in test_data]

print(f"Running inference on {len(X)} fresh queries...")
probs = model.predict_proba(X)
preds = model.predict(X)
classes = list(model.classes_)
realtime_idx = classes.index("realtime")

correct = 0
confidences = []
failures = []

for i, (text, true_lbl, pred_lbl, prob_dist) in enumerate(zip(X, y_true, preds, probs)):
    pred_conf = float(np.max(prob_dist))
    rt_conf = float(prob_dist[realtime_idx])
    confidences.append(pred_conf)
    
    if pred_lbl == true_lbl:
        correct += 1
    else:
        failures.append({
            "index": i + 1,
            "text": text,
            "true_intent": true_lbl,
            "predicted_intent": pred_lbl,
            "predicted_confidence": round(pred_conf * 100, 2),
            "realtime_confidence": round(rt_conf * 100, 2)
        })

accuracy = (correct / len(test_data)) * 100.0
avg_conf = float(np.mean(confidences)) * 100.0
min_conf = float(np.min(confidences)) * 100.0

print("\n" + "=" * 75)
print(f"  HONEST FRESH-TEST-SET RESULTS ({len(test_data)} untouched queries)")
print("=" * 75)
print(f"Accuracy / Recall:  {accuracy:.2f}% ({correct}/{len(test_data)})")
print(f"Average Confidence: {avg_conf:.2f}%")
print(f"Minimum Confidence: {min_conf:.2f}%")
print(f"Total Failures:     {len(failures)}")

if failures:
    print("\n--- DETAILED LIST OF FAILURES ---")
    for f in failures:
        print(f"#{f['index']}: \"{f['text']}\"")
        print(f"   Predicted: {f['predicted_intent']} ({f['predicted_confidence']}%)")
        print(f"   Expected:  {f['true_intent']} (assigned: {f['realtime_confidence']}%)")
else:
    print("\nAll 150 fresh untouched queries were correctly classified as 'realtime'!")

# Save evaluation report to JSON
report = {
    "fresh_test_set_size": len(test_data),
    "overlap_with_train": len(overlaps),
    "accuracy": round(accuracy, 2),
    "average_confidence": round(avg_conf, 2),
    "min_confidence": round(min_conf, 2),
    "num_failures": len(failures),
    "failures": failures
}

out_report_path = os.path.join(DATA_DIR, "fresh_mandi_test_evaluation_report.json")
with open(out_report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\nDetailed evaluation report saved to: {out_report_path}")
