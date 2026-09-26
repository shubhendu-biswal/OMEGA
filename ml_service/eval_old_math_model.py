import os
import sys
import re
import json
import joblib
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

print("=" * 60)
print("  RIGOROUS EVALUATION OF EXISTING MATH MODEL")
print("=" * 60)

# Load existing model assets
vec = joblib.load(os.path.join(ASSETS_DIR, "math_vectorizer.pkl"))
mat = joblib.load(os.path.join(ASSETS_DIR, "math_matrix.pkl"))
answers = joblib.load(os.path.join(ASSETS_DIR, "math_answers.pkl"))

def extract_final_number(text):
    if not isinstance(text, str) or not text.strip():
        return None
    # Look for patterns like "= 123", "= $123.45", "is 123", "#### 123"
    eq_matches = re.findall(r'=\s*(-?\$?[\d\.,]+)', text)
    if eq_matches:
        raw = eq_matches[-1].replace('$', '').replace(',', '').strip().rstrip('.')
        try:
            return round(float(raw), 2)
        except ValueError:
            pass

    hash_match = re.search(r'####\s*(-?[\d\.,]+)', text)
    if hash_match:
        try:
            return round(float(hash_match.group(1).replace(',', '').strip()), 2)
        except ValueError:
            pass

    all_nums = re.findall(r'-?\d+(?:\.\d+)?', text)
    if all_nums:
        try:
            return round(float(all_nums[-1]), 2)
        except ValueError:
            pass
            
    return None

def predict_old_model(query):
    q_vec = vec.transform([query])
    sims = mat.dot(q_vec.T).toarray().ravel()
    best_idx = int(np.argmax(sims))
    max_sim = float(sims[best_idx])
    pred_ans = str(answers[best_idx])
    return best_idx, max_sim, pred_ans

# 1. Evaluate on Training Data Sample (500 rows)
print("\n[1/4] Evaluating on Training Data Sample (500 rows)...")
with open(os.path.join(DATA_DIR, "math_db_train_clean.json"), "r", encoding="utf-8") as f:
    train_data = json.load(f)

np.random.seed(42)
train_sample = np.random.choice(train_data, size=min(500, len(train_data)), replace=False)

train_correct = 0
for item in train_sample:
    q = item['question']
    gt_sol = item['solution']
    gt_val = extract_final_number(gt_sol)
    
    _, _, pred_sol = predict_old_model(q)
    pred_val = extract_final_number(pred_sol)
    
    # In training, the exact question is indexed, so exact retrieval should give 100% or close
    if pred_sol == gt_sol or (gt_val is not None and pred_val is not None and abs(gt_val - pred_val) < 1e-2):
        train_correct += 1

train_acc = train_correct / len(train_sample)
print(f"  Training Sample Accuracy: {train_acc * 100:.2f}% ({train_correct}/{len(train_sample)})")

# 2. Evaluate on Database Template-Held-Out Test Set (500 rows)
print("\n[2/4] Evaluating on Database Template-Held-Out Test Set (500 rows)...")
with open(os.path.join(DATA_DIR, "math_db_held_out_eval.json"), "r", encoding="utf-8") as f:
    held_out_data = json.load(f)

held_out_correct = 0
failures_held_out = []
for item in held_out_data:
    q = item['question']
    gt_sol = item['solution']
    gt_val = extract_final_number(gt_sol)
    
    best_idx, sim, pred_sol = predict_old_model(q)
    pred_val = extract_final_number(pred_sol)
    
    matched = (gt_val is not None and pred_val is not None and abs(gt_val - pred_val) < 1e-2)
    if matched:
        held_out_correct += 1
    else:
        failures_held_out.append({
            "dataset": "Template-Held-Out DB",
            "question": q,
            "expected_val": str(gt_val),
            "predicted_val": str(pred_val),
            "expected_solution": gt_sol,
            "predicted_solution": pred_sol,
            "similarity": sim
        })

held_out_acc = held_out_correct / len(held_out_data)
print(f"  Held-Out DB Test Accuracy: {held_out_acc * 100:.2f}% ({held_out_correct}/{len(held_out_data)})")

# 3. Evaluate on 200 Natural Hand-Written Math Word Problems
print("\n[3/4] Evaluating on 200 Natural Hand-Written Math Problems...")
with open(os.path.join(DATA_DIR, "natural_200_test.json"), "r", encoding="utf-8") as f:
    natural_data = json.load(f)

natural_correct = 0
failures_natural = []
for item in natural_data:
    q = item['question']
    gt_val = float(item['ground_truth'])
    best_idx, sim, pred_sol = predict_old_model(q)
    pred_val = extract_final_number(pred_sol)
    
    matched = (pred_val is not None and abs(gt_val - pred_val) < 1e-2)
    if matched:
        natural_correct += 1
    else:
        failures_natural.append({
            "dataset": "Natural Word Problems",
            "question": q,
            "expected_val": str(gt_val),
            "predicted_val": str(pred_val),
            "predicted_solution": pred_sol,
            "similarity": sim
        })

natural_acc = natural_correct / len(natural_data)
print(f"  Natural Test Accuracy: {natural_acc * 100:.2f}% ({natural_correct}/{len(natural_data)})")

# 4. Evaluate on 200 GSM8K Test Problems
print("\n[4/4] Evaluating on 200 GSM8K Test Problems...")
with open(os.path.join(DATA_DIR, "gsm8k_200_test.json"), "r", encoding="utf-8") as f:
    gsm8k_data = json.load(f)

gsm8k_correct = 0
failures_gsm8k = []
for item in gsm8k_data:
    q = item['question']
    try:
        gt_val = float(item['ground_truth'])
    except ValueError:
        gt_val = None
        
    best_idx, sim, pred_sol = predict_old_model(q)
    pred_val = extract_final_number(pred_sol)
    
    matched = (gt_val is not None and pred_val is not None and abs(gt_val - pred_val) < 1e-2)
    if matched:
        gsm8k_correct += 1
    else:
        failures_gsm8k.append({
            "dataset": "GSM8K Test",
            "question": q,
            "expected_val": str(gt_val),
            "predicted_val": str(pred_val),
            "predicted_solution": pred_sol,
            "similarity": sim
        })

gsm8k_acc = gsm8k_correct / len(gsm8k_data)
print(f"  GSM8K Test Accuracy: {gsm8k_acc * 100:.2f}% ({gsm8k_correct}/{len(gsm8k_data)})")

combined_natural_gsm8k_acc = (natural_correct + gsm8k_correct) / (len(natural_data) + len(gsm8k_data))

# Summary Table
print("\n" + "=" * 70)
print("  EXISTING MATH MODEL EVALUATION RESULTS (RIGOROUS NUMERICAL ACCURACY)")
print("=" * 70)
summary_table = pd.DataFrame([
    {"Dataset / Split": "Training Data Sample", "Size": len(train_sample), "Accuracy (%)": f"{train_acc * 100:.2f}%", "Method": "TF-IDF Nearest Neighbor Retrieval"},
    {"Dataset / Split": "Template-Held-Out DB Split", "Size": len(held_out_data), "Accuracy (%)": f"{held_out_acc * 100:.2f}%", "Method": "TF-IDF Nearest Neighbor Retrieval"},
    {"Dataset / Split": "Natural Math Word Problems", "Size": len(natural_data), "Accuracy (%)": f"{natural_acc * 100:.2f}%", "Method": "TF-IDF Nearest Neighbor Retrieval"},
    {"Dataset / Split": "GSM8K Test Sample", "Size": len(gsm8k_data), "Accuracy (%)": f"{gsm8k_acc * 100:.2f}%", "Method": "TF-IDF Nearest Neighbor Retrieval"},
    {"Dataset / Split": "Combined Natural + GSM8K", "Size": len(natural_data) + len(gsm8k_data), "Accuracy (%)": f"{combined_natural_gsm8k_acc * 100:.2f}%", "Method": "TF-IDF Nearest Neighbor Retrieval"},
])
print(summary_table.to_string(index=False))

# 20 Failure Examples (sampled across held-out, natural, and GSM8K)
all_failures = failures_held_out + failures_natural + failures_gsm8k
np.random.seed(42)
sampled_20_failures = np.random.choice(all_failures, size=min(20, len(all_failures)), replace=False).tolist()

print("\n" + "=" * 70)
print("  20 REPRESENTATIVE FAILURE EXAMPLES OF EXISTING MODEL")
print("=" * 70)
for idx, fail in enumerate(sampled_20_failures, 1):
    print(f"\n--- Failure Example #{idx:02d} [{fail['dataset']}] ---")
    print(f"  Question:            {fail['question']}")
    print(f"  Expected Value:      {fail.get('expected_val', 'N/A')}")
    print(f"  Predicted Value:     {fail.get('predicted_val', 'N/A')}")
    print(f"  Retrieved Solution:  {fail['predicted_solution'][:110]}...")
    print(f"  Cosine Similarity:   {fail['similarity']:.4f}")

eval_results = {
    "summary": summary_table.to_dict(orient="records"),
    "failures_20": sampled_20_failures
}
with open(os.path.join(DATA_DIR, "old_model_eval_results.json"), "w", encoding="utf-8") as f:
    json.dump(eval_results, f, indent=2)
