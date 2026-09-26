import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

# Ensure path has ml_service
sys.path.insert(0, os.path.dirname(__file__))
from assets.v2.math_solver.solver import OmegaMathSolver

solver = OmegaMathSolver()

with open("data/natural_200_test.json", "r", encoding="utf-8") as f:
    natural_data = json.load(f)

correct = 0
failures = []

for idx, item in enumerate(natural_data, 1):
    q = item['question']
    gt = float(item['ground_truth'])
    res = solver.solve(q)
    out = res['final_answer']
    
    # Extract final number from output
    nums = re.findall(r'-?\d+(?:\.\d+)?', out)
    matched = False
    if nums:
        try:
            pred_val = float(nums[-1])
            if abs(pred_val - gt) < 1e-2:
                matched = True
        except ValueError:
            pass
            
    if matched:
        correct += 1
    else:
        failures.append({
            "id": item['id'],
            "category": item.get('category'),
            "question": q,
            "ground_truth": gt,
            "output": out,
            "error": res.get('error'),
            "code": res.get('code')
        })

print(f"Natural Problems Test: {correct}/{len(natural_data)} ({correct/len(natural_data)*100:.2f}%)")
if failures:
    print(f"First 5 failures:")
    for f in failures[:5]:
        print(f"[{f['category']}] Q: {f['question'][:60]} | GT: {f['ground_truth']} | Out: {f['output']}")
        print(f"Code:\n{f['code']}\nErr: {f['error']}")
