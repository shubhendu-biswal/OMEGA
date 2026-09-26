import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from assets.v2.math_solver.solver import OmegaMathSolver
solver = OmegaMathSolver()

with open("data/gsm8k_200_test.json", "r", encoding="utf-8") as f:
    gsm8k_data = json.load(f)

def extract_final_number(text):
    if not isinstance(text, str) or not text.strip():
        return None
    eq_matches = re.findall(r'=\s*(-?\$?[\d\.,]+)', text)
    if eq_matches:
        raw = eq_matches[-1].replace('$', '').replace(',', '').strip().rstrip('.')
        try:
            return round(float(raw), 2)
        except ValueError:
            pass
    all_nums = re.findall(r'-?\d+(?:\.\d+)?', text)
    if all_nums:
        try:
            return round(float(all_nums[-1]), 2)
        except ValueError:
            pass
    return None

correct = 0
failures = []

for idx, item in enumerate(gsm8k_data, 1):
    q = item['question']
    gt_val_s = item['ground_truth']
    try:
        gt_val = float(gt_val_s)
    except ValueError:
        gt_val = None
        
    res = solver.solve(q)
    out = res['final_answer']
    pred_val = extract_final_number(out)
    
    matched = False
    if gt_val is not None and pred_val is not None and abs(gt_val - pred_val) < 1e-2:
        matched = True
        
    if matched:
        correct += 1
    else:
        failures.append({
            "id": item.get('id'),
            "question": q,
            "gt_val": gt_val,
            "out": out,
            "pred_val": pred_val,
            "code": res.get('code')
        })

print(f"GSM8K Test (200 problems): {correct}/{len(gsm8k_data)} ({correct/len(gsm8k_data)*100:.2f}%)")
if failures:
    print(f"Failures count: {len(failures)}")
    print(f"Sample 5 failures:")
    for f in failures[:5]:
        print(f"Q: {f['question'][:70]}... | GT: {f['gt_val']} | Out: {f['out']}")
