import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from assets.v2.math_solver.solver import OmegaMathSolver
solver = OmegaMathSolver()

with open("data/math_db_held_out_eval.json", "r", encoding="utf-8") as f:
    held_out_data = json.load(f)

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

for idx, item in enumerate(held_out_data, 1):
    q = item['question']
    gt_sol = item['solution']
    gt_val = extract_final_number(gt_sol)
    
    res = solver.solve(q)
    out = res['final_answer']
    pred_val = extract_final_number(out)
    
    matched = False
    if gt_val is not None and pred_val is not None and abs(gt_val - pred_val) < 1e-2:
        matched = True
    elif gt_sol and out and (out in gt_sol or gt_sol in out):
        matched = True
        
    if matched:
        correct += 1
    else:
        failures.append({
            "id": item.get('id'),
            "template": item.get('template'),
            "question": q,
            "gt_sol": gt_sol,
            "gt_val": gt_val,
            "out": out,
            "pred_val": pred_val,
            "code": res.get('code')
        })

print(f"Database Held-Out Test: {correct}/{len(held_out_data)} ({correct/len(held_out_data)*100:.2f}%)")
if failures:
    print(f"Failures count: {len(failures)}")
    print(f"Sample failures:")
    for f in failures[:5]:
        print(f"[{f['template']}] Q: {f['question']} | GT: {f['gt_val']} | Out: {f['out']}")
