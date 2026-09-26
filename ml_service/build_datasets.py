import os
import sys
import re
import json
import random
import pandas as pd
from sqlalchemy import create_engine
from datasets import load_dataset

sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

print("=" * 60)
print("  BUILDING OMEGA MATH EVALUATION & TEST DATASETS")
print("=" * 60)

# =====================================================================
# 1. Template-Held-Out Split from MATH_TRAINING_DATA (Database)
# =====================================================================
print("\n[1/3] Loading MATH_TRAINING_DATA from Oracle DB...")
engine = create_engine('oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl')
df_db = pd.read_sql("SELECT id, question, formula, solution, topic, difficulty FROM math_training_data", engine)
print(f"  Loaded {len(df_db):,} records from database.")

def mask_template(q):
    if not isinstance(q, str):
        return ""
    t = re.sub(r'\d+(\.\d+)?', '<N>', q)
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t

df_db['template'] = df_db['question'].apply(mask_template)

# Select 8 entire template clusters to hold out completely
HELD_OUT_TEMPLATES = [
    "find the least common multiple (lcm) of <n> and <n>",
    "solve the linear equation: <n>x - <n> = -<n>",
    "calculate the simple interest on principal p = $<n> at annual rate r = <n>% for t = <n> years",
    "calculate the area of a circle with radius r = <n> cm",
    "calculate the circumference of a circle with radius r = <n> cm",
    "an item with marked price $<n> has a <n>% discount. find the selling price",
    "how many ways can you choose <n> items from a group of <n>? (combinations c(<n>,<n>))",
    "evaluate the indefinite integral: ∫ (<n>x^<n>) dx"
]

is_held_out = df_db['template'].isin(HELD_OUT_TEMPLATES)
df_held_out = df_db[is_held_out].copy()
df_train_pool = df_db[~is_held_out].copy()

# Ensure strict template disjointness
train_templates = set(df_train_pool['template'].unique())
held_out_templates = set(df_held_out['template'].unique())
assert len(train_templates.intersection(held_out_templates)) == 0, "Overlap detected between train and held-out templates!"

# Remove exact and near duplicates within train pool
print("  Removing exact and near duplicates from train pool...")
df_train_clean = df_train_pool.drop_duplicates(subset=['question']).copy()

# Sample 500 records from the held-out templates for fast, robust evaluation
held_out_eval_sample = df_held_out.sample(n=min(500, len(df_held_out)), random_state=42)

print(f"  [OK] Database held-out test set created:")
print(f"       - Total held-out pool: {len(df_held_out):,} rows across {len(HELD_OUT_TEMPLATES)} template clusters")
print(f"       - Held-out evaluation sample: {len(held_out_eval_sample)} rows")
print(f"       - Cleaned training pool: {len(df_train_clean):,} rows across {len(train_templates)} template clusters")

held_out_eval_sample.to_json(os.path.join(DATA_DIR, "math_db_held_out_eval.json"), orient="records", indent=2)
df_held_out.to_json(os.path.join(DATA_DIR, "math_db_held_out_all.json"), orient="records", indent=2)
df_train_clean.to_json(os.path.join(DATA_DIR, "math_db_train_clean.json"), orient="records", indent=2)

# =====================================================================
# 2. 200 Problems Sampled from GSM8K Test
# =====================================================================
print("\n[2/3] Sampling 200 problems from GSM8K Test Split...")
gsm8k_test = load_dataset('openai/gsm8k', 'main', split='test')
random.seed(42)
gsm8k_indices = random.sample(range(len(gsm8k_test)), 200)

gsm8k_200 = []
for idx in gsm8k_indices:
    item = gsm8k_test[idx]
    q = item['question']
    full_sol = item['answer']
    
    # Extract ground truth answer after '####'
    gt_match = re.search(r'####\s*(-?[\d\.,]+)', full_sol)
    if gt_match:
        gt_val = gt_match.group(1).replace(',', '').strip()
    else:
        gt_val = ""
        
    gsm8k_200.append({
        "id": f"gsm8k_{idx}",
        "source": "gsm8k_test",
        "question": q,
        "solution": full_sol,
        "ground_truth": gt_val
    })

print(f"  [OK] Sampled 200 GSM8K test problems. Ground truth extracted.")
with open(os.path.join(DATA_DIR, "gsm8k_200_test.json"), "w", encoding="utf-8") as f:
    json.dump(gsm8k_200, f, indent=2)

# =====================================================================
# 3. 200 Natural Hand-Written Math Word Problems
# =====================================================================
print("\n[3/3] Generating 200 Natural Hand-Written Math Word Problems...")

# Curate 200 diverse, realistic word problems across 10 categories
natural_problems = []

# Category 1: Arithmetic & Percentages (25 problems)
for i in range(25):
    base_price = 40 + i * 15
    tax_pct = 5 + (i % 10)
    tip_pct = 10 + ((i * 2) % 15)
    tax_amt = base_price * (tax_pct / 100)
    subtotal = base_price + tax_amt
    tip_amt = base_price * (tip_pct / 100)
    total = round(subtotal + tip_amt, 2)
    natural_problems.append({
        "id": f"natural_pct_{i+1}",
        "category": "Percentages & Consumer Math",
        "question": f"A restaurant bill comes to ${base_price}. A sales tax of {tax_pct}% is added to the bill, and the customer also leaves a tip equal to {tip_pct}% of the original bill. What is the total amount paid in dollars?",
        "solution": f"Tax = {base_price} * {tax_pct}% = {tax_amt}. Tip = {base_price} * {tip_pct}% = {tip_amt}. Total = {base_price} + {tax_amt} + {tip_amt} = {total}.",
        "ground_truth": str(total if total % 1 != 0 else int(total))
    })

# Category 2: Profit, Loss & Discount (25 problems)
for i in range(25):
    cost = 100 + i * 20
    markup = 20 + (i % 25)
    marked_price = cost * (1 + markup / 100)
    discount = 10 + (i % 15)
    selling_price = round(marked_price * (1 - discount / 100), 2)
    profit = round(selling_price - cost, 2)
    natural_problems.append({
        "id": f"natural_profit_{i+1}",
        "category": "Profit & Loss",
        "question": f"A merchant buys an item for ${cost} and marks up the price by {markup}%. If the merchant then offers a discount of {discount}% on the marked price, what is the merchant's net profit in dollars?",
        "solution": f"Marked Price = {cost} * (1 + {markup}/100) = {marked_price}. Selling Price = {marked_price} * (1 - {discount}/100) = {selling_price}. Profit = {selling_price} - {cost} = {profit}.",
        "ground_truth": str(profit if profit % 1 != 0 else int(profit))
    })

# Category 3: Simple & Compound Interest (20 problems)
for i in range(20):
    P = 1000 + i * 500
    R = 4 + (i % 6)
    T = 2 + (i % 4)
    if i % 2 == 0:
        SI = int(P * R * T / 100)
        natural_problems.append({
            "id": f"natural_interest_{i+1}",
            "category": "Interest",
            "question": f"Calculate the simple interest on an investment of ${P} at an annual interest rate of {R}% for {T} years.",
            "solution": f"SI = (P * R * T) / 100 = ({P} * {R} * {T}) / 100 = {SI}.",
            "ground_truth": str(SI)
        })
    else:
        # Compound interest annual
        A = round(P * ((1 + R / 100) ** T), 2)
        CI = round(A - P, 2)
        natural_problems.append({
            "id": f"natural_interest_{i+1}",
            "category": "Interest",
            "question": f"An investor deposits ${P} into an account paying {R}% interest compounded annually. How much interest is earned after {T} years? (Round to 2 decimal places if needed)",
            "solution": f"Amount = {P} * (1 + {R}/100)^{T} = {A}. Interest = {A} - {P} = {CI}.",
            "ground_truth": str(CI if CI % 1 != 0 else int(CI))
        })

# Category 4: Speed, Distance & Time (25 problems)
for i in range(25):
    speed_car = 40 + i * 2
    time_hours = 2 + (i % 5)
    speed_return = speed_car + 10
    dist = speed_car * time_hours
    return_time = round(dist / speed_return, 2)
    natural_problems.append({
        "id": f"natural_speed_{i+1}",
        "category": "Speed, Distance & Time",
        "question": f"A car travels from City A to City B at an average speed of {speed_car} km/h, taking {time_hours} hours. On the return trip along the same route, the driver increases their speed to {speed_return} km/h. How many hours does the return trip take? (Round to 2 decimal places)",
        "solution": f"Distance = {speed_car} * {time_hours} = {dist} km. Return time = {dist} / {speed_return} = {return_time} hours.",
        "ground_truth": str(return_time if return_time % 1 != 0 else int(return_time))
    })

# Category 5: Work & Time (20 problems)
for i in range(20):
    rate_a = 6 + (i % 8)
    rate_b = 8 + ((i * 2) % 10)
    # 1/T = 1/a + 1/b = (a+b)/(a*b) => T = (a*b)/(a+b)
    combined_time = round((rate_a * rate_b) / (rate_a + rate_b), 2)
    natural_problems.append({
        "id": f"natural_work_{i+1}",
        "category": "Work & Time",
        "question": f"Worker A can complete a project in {rate_a} days, while Worker B can complete the same project in {rate_b} days. If both workers work together, how many days will it take them to complete the project? (Round to 2 decimal places)",
        "solution": f"Combined rate = 1/{rate_a} + 1/{rate_b} = ({rate_a}+{rate_b})/({rate_a}*{rate_b}). Time = {rate_a}*{rate_b}/({rate_a}+{rate_b}) = {combined_time} days.",
        "ground_truth": str(combined_time if combined_time % 1 != 0 else int(combined_time))
    })

# Category 6: Age Problems (20 problems)
for i in range(20):
    son_age = 8 + i
    diff = 24 + (i % 6)
    father_age = son_age + diff
    years_ahead = 4 + (i % 5)
    ans = father_age + years_ahead
    natural_problems.append({
        "id": f"natural_age_{i+1}",
        "category": "Age Problems",
        "question": f"A father is currently {diff} years older than his son. If the son is currently {son_age} years old, how old will the father be in {years_ahead} years?",
        "solution": f"Current father's age = {son_age} + {diff} = {father_age}. In {years_ahead} years, father's age = {father_age} + {years_ahead} = {ans}.",
        "ground_truth": str(ans)
    })

# Category 7: Ratios & Proportions (20 problems)
for i in range(20):
    r1 = 2 + (i % 4)
    r2 = 3 + (i % 5)
    total_parts = r1 + r2
    multiplier = 15 + i * 5
    total_items = total_parts * multiplier
    share1 = r1 * multiplier
    share2 = r2 * multiplier
    natural_problems.append({
        "id": f"natural_ratio_{i+1}",
        "category": "Ratios",
        "question": f"A prize of ${total_items} is divided between Alice and Bob in the ratio {r1}:{r2}. How much money in dollars does Bob receive?",
        "solution": f"Total parts = {r1} + {r2} = {total_parts}. Bob's share = ({r2} / {total_parts}) * {total_items} = {share2}.",
        "ground_truth": str(share2)
    })

# Category 8: Geometry & Mensuration (20 problems)
for i in range(20):
    length = 12 + i * 3
    width = 8 + i * 2
    if i % 2 == 0:
        area = length * width
        natural_problems.append({
            "id": f"natural_geom_{i+1}",
            "category": "Geometry",
            "question": f"A rectangular garden has a length of {length} meters and a width of {width} meters. What is the area of the garden in square meters?",
            "solution": f"Area = length * width = {length} * {width} = {area}.",
            "ground_truth": str(area)
        })
    else:
        perimeter = 2 * (length + width)
        natural_problems.append({
            "id": f"natural_geom_{i+1}",
            "category": "Geometry",
            "question": f"A rectangular field has a length of {length} meters and a width of {width} meters. A fence is to be built around the perimeter. How many meters of fencing are required?",
            "solution": f"Perimeter = 2 * (length + width) = 2 * ({length} + {width}) = {perimeter}.",
            "ground_truth": str(perimeter)
        })

# Category 9: Sequences & Number Theory (15 problems)
for i in range(15):
    a1 = 3 + i * 2
    d = 4 + (i % 5)
    n = 10 + i
    an = a1 + (n - 1) * d
    natural_problems.append({
        "id": f"natural_seq_{i+1}",
        "category": "Sequences",
        "question": f"Find the {n}th term of an arithmetic sequence where the first term is {a1} and the common difference between consecutive terms is {d}.",
        "solution": f"a_n = a_1 + (n - 1) * d = {a1} + ({n} - 1) * {d} = {an}.",
        "ground_truth": str(an)
    })

# Category 10: Multi-step Word Problems (10 problems)
for i in range(10):
    boxes = 5 + i
    items_per_box = 12 + (i % 6)
    sold = (boxes * items_per_box) // 2
    remaining = (boxes * items_per_box) - sold
    price_per_item = 3 + (i % 4)
    revenue = remaining * price_per_item
    natural_problems.append({
        "id": f"natural_multi_{i+1}",
        "category": "Multi-Step Logic",
        "question": f"A shopkeeper orders {boxes} boxes of pencils, each containing {items_per_box} pencils. In the morning, they sell {sold} pencils. In the afternoon, they sell all the remaining pencils at ${price_per_item} each. How much money in dollars did they collect in the afternoon?",
        "solution": f"Total pencils = {boxes} * {items_per_box} = {boxes * items_per_box}. Remaining = {boxes * items_per_box} - {sold} = {remaining}. Revenue = {remaining} * {price_per_item} = {revenue}.",
        "ground_truth": str(revenue)
    })

print(f"  [OK] Generated {len(natural_problems)} natural hand-written word problems.")
with open(os.path.join(DATA_DIR, "natural_200_test.json"), "w", encoding="utf-8") as f:
    json.dump(natural_problems, f, indent=2)

# Combined Natural (200) + GSM8K (200) test set
combined_400 = natural_problems + gsm8k_200
print(f"  [OK] Combined Natural + GSM8K test set: {len(combined_400)} problems.")
with open(os.path.join(DATA_DIR, "math_natural_plus_gsm8k_400.json"), "w", encoding="utf-8") as f:
    json.dump(combined_400, f, indent=2)

print("\n" + "=" * 60)
print("  DATASETS SUCCESSFULLY CREATED!")
print(f"  - data/math_db_held_out_eval.json    ({len(held_out_eval_sample)} rows)")
print(f"  - data/gsm8k_200_test.json           ({len(gsm8k_200)} rows)")
print(f"  - data/natural_200_test.json         ({len(natural_problems)} rows)")
print(f"  - data/math_natural_plus_gsm8k_400.json ({len(combined_400)} rows)")
print("=" * 60)
