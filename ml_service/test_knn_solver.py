import os
import sys
import re
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sandbox import execute_in_sandbox

sys.stdout.reconfigure(encoding='utf-8')

# Load the 4,750 verified training examples
with open("data/math_solver_verified_train.json", "r", encoding="utf-8") as f:
    train_data = json.load(f)

print(f"Loaded {len(train_data)} verified training examples.")

# Build TF-IDF index over normalized question templates
def normalize_question(q):
    # Mask numbers to capture the mathematical structure
    norm = re.sub(r'\$?\d+(?:\.\d+)?', '<N>', q.lower())
    return norm

train_norm_questions = [normalize_question(item['question']) for item in train_data]

vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=15000, sublinear_tf=True)
X_train = vectorizer.fit_transform(train_norm_questions)
print(f"Matrix shape: {X_train.shape}")

# Test on 20 GSM8K test examples
with open("data/gsm8k_200_test.json", "r", encoding="utf-8") as f:
    test_data = json.load(f)[:20]

correct = 0
for idx, item in enumerate(test_data, 1):
    q = item['question']
    gt = float(item['ground_truth'])
    
    q_norm = normalize_question(q)
    q_vec = vectorizer.transform([q_norm])
    sims = X_train.dot(q_vec.T).toarray().ravel()
    best_idx = int(np.argmax(sims))
    best_sim = float(sims[best_idx])
    
    matched_example = train_data[best_idx]
    
    # Adapt code: extract numbers from query
    q_nums = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', q.replace('$', '').replace(',', ''))]
    code_templ = matched_example['code']
    
    # Try running the adapted or matched code
    # If high similarity, run code with query numbers
    s, out, err = execute_in_sandbox(code_templ)
    pred_val = None
    if s and out:
        nums_out = re.findall(r'-?\d+(?:\.\d+)?', out)
        if nums_out:
            try:
                pred_val = float(nums_out[-1])
            except ValueError:
                pass
                
    matched = (pred_val is not None and abs(pred_val - gt) < 1e-2)
    if matched:
        correct += 1
    print(f"[{idx:02d}] Sim: {best_sim:.3f} | GT: {gt} | Pred: {pred_val} | Match: {matched}")

print(f"Sample Accuracy: {correct}/{len(test_data)} ({correct/len(test_data)*100:.1f}%)")
