import os
import sys
import re
import json
import random
import numpy as np
import pandas as pd
from datasets import load_dataset
from sandbox import execute_in_sandbox

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

print("=" * 65)
print("  SYNTHESIZING VERIFIED CODE-AUGMENTED MATH TRAINING DATA")
print("=" * 65)

# 1. Database clean train set
print("\n[1/3] Processing clean DB training pool...")
with open(os.path.join(DATA_DIR, "math_db_train_clean.json"), "r", encoding="utf-8") as f:
    db_rows = json.load(f)

def generate_python_code_for_db_row(q, formula, sol, topic):
    """
    Generates deterministic, robust Python/SymPy calculation code
    for database math problems based on question structure.
    """
    q_lower = q.lower()
    
    # Linear equation: e.g. Solve the linear equation: 4x - 29 = 27
    m_eq = re.search(r'(\d+)x\s*([\+\-])\s*(\d+)\s*=\s*(-?\d+)', q)
    if m_eq:
        a, op, b, c = m_eq.groups()
        sign = '-' if op == '+' else '+' # moving b to other side
        code = f"x = ({c} {sign} {b}) / {a}\nprint(round(x, 2))"
        reasoning = f"To solve {a}x {op} {b} = {c}, we isolate x by applying inverse operations."
        return reasoning, code

    # Mode of dataset: identify the mode of the dataset: [1, 2, 2, 3]
    m_mode = re.search(r'\[(.*?)\]', q)
    if 'mode' in q_lower and m_mode:
        nums_str = m_mode.group(1)
        code = f"import statistics\ndata = [{nums_str}]\nprint(statistics.mode(data))"
        reasoning = "The mode is the value that appears most frequently in the dataset."
        return reasoning, code

    # GCD / HCF: find the greatest common divisor (gcd/hcf) of 48 and 180
    m_gcd = re.search(r'of\s+(\d+)\s+and\s+(\d+)', q_lower)
    if 'greatest common divisor' in q_lower or 'gcd' in q_lower:
        if m_gcd:
            n1, n2 = m_gcd.groups()
            code = f"import math\nprint(math.gcd({n1}, {n2}))"
            reasoning = f"We compute the greatest common divisor of {n1} and {n2} using the Euclidean algorithm."
            return reasoning, code

    # Profit & Profit %: if cost price (cp) is $108 and selling price (sp) is $347
    m_profit = re.search(r'cp\D+(\d+)\D+sp\D+(\d+)', q_lower)
    if m_profit:
        cp, sp = m_profit.groups()
        code = f"cp = {cp}\nsp = {sp}\nprofit = sp - cp\nprofit_pct = round((profit / cp) * 100, 1)\nprint(f'Profit: ${{profit}}, Profit %: ${{profit_pct}}%')"
        reasoning = f"Profit equals selling price minus cost price, and profit percentage is (profit / cost price) * 100."
        return reasoning, code

    # Percentage: what is 10% of 1769?
    m_pct = re.search(r'(\d+(?:\.\d+)?)%\s+of\s+(\d+(?:\.\d+)?)', q_lower)
    if m_pct:
        pct, val = m_pct.groups()
        code = f"result = ({pct} / 100) * {val}\nprint(round(result, 2))"
        reasoning = f"To find {pct}% of {val}, multiply {val} by {pct}/100."
        return reasoning, code

    # Arithmetic: add, multiply, divide, subtract
    m_add = re.search(r'what is\s+(\d+)\s*\+\s*(\d+)', q_lower)
    if m_add:
        n1, n2 = m_add.groups()
        code = f"print({n1} + {n2})"
        reasoning = f"Add the two numbers: {n1} + {n2}."
        return reasoning, code

    m_mul = re.search(r'multiply\s+(\d+)\s+by\s+(\d+)', q_lower)
    if m_mul:
        n1, n2 = m_mul.groups()
        code = f"print({n1} * {n2})"
        reasoning = f"Compute the product: {n1} * {n2}."
        return reasoning, code

    m_mod = re.search(r'remainder when\s+(\d+)\s+is divided by\s+(\d+)', q_lower)
    if m_mod:
        n1, n2 = m_mod.groups()
        code = f"print({n1} % {n2})"
        reasoning = f"The remainder is the modulo operation: {n1} % {n2}."
        return reasoning, code

    # Geometry: rectangle area and perimeter
    m_rect = re.search(r'length\s+(\d+)\s*m\s+and\s+width\s+(\d+)\s*m', q_lower)
    if m_rect:
        l, w = m_rect.groups()
        code = f"length = {l}\nwidth = {w}\narea = length * width\nperimeter = 2 * (length + width)\nprint(f'Area: ${{area}}, Perimeter: ${{perimeter}}')"
        reasoning = "Area of a rectangle is length * width, and perimeter is 2 * (length + width)."
        return reasoning, code

    # Geometry: triangle area
    m_tri = re.search(r'base\s+(\d+)\s*cm\s+and\s+perpendicular height\s+(\d+)\s*cm', q_lower)
    if m_tri:
        b, h = m_tri.groups()
        code = f"area = 0.5 * {b} * {h}\nprint(round(area, 2))"
        reasoning = "The area of a triangle is 0.5 * base * height."
        return reasoning, code

    # Geometry: cylinder volume
    m_cyl = re.search(r'radius\s+(\d+)\s*cm\s+and\s+height\s+(\d+)\s*cm', q_lower)
    if m_cyl and 'cylinder' in q_lower:
        r, h = m_cyl.groups()
        code = f"import math\nvolume = math.pi * ({r}**2) * {h}\nprint(round(volume, 2))"
        reasoning = "The volume of a cylinder is pi * r^2 * h."
        return reasoning, code

    # Calculus: derivative
    m_diff = re.search(r'derivative of f\(x\)\s*=\s*(\d+)x\^(\d+)\s*\+\s*(\d+)', q_lower)
    if m_diff:
        c, p, const = m_diff.groups()
        new_c = int(c) * int(p)
        new_p = int(p) - 1
        code = f"import sympy\nx = sympy.Symbol('x')\nf = {c}*x**{p} + {const}\nprint(sympy.diff(f, x))"
        reasoning = f"Using the power rule, the derivative of {c}x^{p} + {const} is {new_c}x^{new_p}."
        return reasoning, code

    # Arithmetic progression nth term
    m_ap = re.search(r'(\d+)th term of an arithmetic progression.*first term a\s*=\s*(\d+).*difference d\s*=\s*(\d+)', q_lower)
    if m_ap:
        n, a, d = m_ap.groups()
        code = f"a = {a}\nd = {d}\nn = {n}\nan = a + (n - 1) * d\nprint(an)"
        reasoning = f"The nth term of an AP is a + (n - 1) * d."
        return reasoning, code

    return None, None

verified_db_examples = []
# Sample a diverse set of 3,000 DB training examples across topics
np.random.seed(42)
sampled_db = np.random.choice(db_rows, size=min(4000, len(db_rows)), replace=False)

for row in sampled_db:
    q = row['question']
    gt_sol = row['solution']
    formula = row.get('formula', '')
    topic = row.get('topic', '')
    
    reasoning, code = generate_python_code_for_db_row(q, formula, gt_sol, topic)
    if not code:
        continue
        
    # Execute in sandbox to verify correctness
    success, output, err = execute_in_sandbox(code)
    if not success or not output:
        continue
        
    # Check if the output matches ground truth
    # Extract numbers from both
    out_nums = re.findall(r'-?\d+(?:\.\d+)?', output)
    gt_nums = re.findall(r'-?\d+(?:\.\d+)?', gt_sol)
    if out_nums and gt_nums:
        # Match if the final numeric answer or major value matches
        if out_nums[-1] in gt_nums or (len(out_nums) > 1 and out_nums[0] in gt_nums):
            verified_db_examples.append({
                "question": q,
                "reasoning": reasoning,
                "code": code,
                "output": output,
                "ground_truth": gt_nums[-1]
            })

print(f"  [OK] Verified {len(verified_db_examples)} code-executable DB training examples.")

# 2. GSM8K Training Data (Augment with step-by-step Python solutions)
print("\n[2/3] Augmenting GSM8K training problems with verified Python code...")
gsm8k_train = load_dataset('openai/gsm8k', 'main', split='train')

def generate_python_for_gsm8k(q, answer_text):
    """Generate Python calculation code for GSM8K word problems."""
    gt_match = re.search(r'####\s*(-?[\d\.,]+)', answer_text)
    if not gt_match:
        return None, None
    gt_val = float(gt_match.group(1).replace(',', '').strip())

    # Extract intermediate calculations like <<16-3-4=9>>
    calcs = re.findall(r'<<([^>]+)>>', answer_text)
    if not calcs:
        return None, None

    code_lines = []
    var_idx = 1
    for calc in calcs:
        if '=' in calc:
            expr, res = calc.split('=', 1)
            # sanitize expr
            expr = expr.strip()
            # replace non-standard operators
            expr = expr.replace('^', '**').replace('x', '*').replace('X', '*')
            # only allow numbers and operators
            if re.match(r'^[\d\.\s\+\-\*\/\(\)]+$', expr):
                code_lines.append(f"step_{var_idx} = {expr}")
                var_idx += 1

    if not code_lines:
        return None, None

    code_lines.append(f"final_answer = step_{var_idx - 1}")
    code_lines.append("print(final_answer)")
    code = "\n".join(code_lines)
    reasoning = "We break down the multi-step word problem into intermediate calculation steps."
    return reasoning, code

verified_gsm8k_examples = []
for idx in range(min(3000, len(gsm8k_train))):
    item = gsm8k_train[idx]
    q = item['question']
    ans = item['answer']
    
    gt_match = re.search(r'####\s*(-?[\d\.,]+)', ans)
    if not gt_match:
        continue
    gt_val = float(gt_match.group(1).replace(',', '').strip())

    reasoning, code = generate_python_for_gsm8k(q, ans)
    if not code:
        continue

    success, output, err = execute_in_sandbox(code)
    if success and output:
        try:
            out_val = float(re.findall(r'-?\d+(?:\.\d+)?', output)[-1])
            if abs(out_val - gt_val) < 1e-2:
                verified_gsm8k_examples.append({
                    "question": q,
                    "reasoning": reasoning,
                    "code": code,
                    "output": str(int(out_val) if out_val.is_integer() else out_val),
                    "ground_truth": str(int(gt_val) if gt_val.is_integer() else gt_val)
                })
        except Exception:
            pass

print(f"  [OK] Verified {len(verified_gsm8k_examples)} code-executable GSM8K training examples.")

# 3. Combine into the unified training format
all_verified = verified_db_examples + verified_gsm8k_examples
print(f"\n[3/3] Total verified code-augmented training records: {len(all_verified):,}")

formatted_dataset = []
for item in all_verified:
    formatted_dataset.append({
        "prompt": f"<|im_start|>system\nYou are an expert mathematical problem solver. When given a problem, provide brief step-by-step reasoning, then a clean Python code block enclosed in ```python ... ``` that calculates the answer, and print the result.<|im_end|>\n<|im_start|>user\n{item['question']}<|im_end|>\n<|im_start|>assistant\nReasoning: {item['reasoning']}\n```python\n{item['code']}\n```\nFinal Answer: {item['output']}<|im_end|>",
        "question": item['question'],
        "reasoning": item['reasoning'],
        "code": item['code'],
        "output": item['output']
    })

train_file = os.path.join(DATA_DIR, "math_solver_verified_train.json")
with open(train_file, "w", encoding="utf-8") as f:
    json.dump(formatted_dataset, f, indent=2)

print(f"  [OK] Successfully saved verified dataset to {train_file}")
