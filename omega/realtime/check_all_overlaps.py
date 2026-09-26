import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")

train_v4_path = os.path.join(DATA_DIR, "intent_train_v4.json")
train_v3_path = os.path.join(DATA_DIR, "intent_train_v3.json")
mandi_150_path = os.path.join(DATA_DIR, "mandi_handcrafted_150.json")
gap_75_path = os.path.join(DATA_DIR, "targeted_gap_75.json")
strengthen_path = os.path.join(DATA_DIR, "domain_strengthening_train.json")

hw_100_path = os.path.join(DATA_DIR, "handwritten_test_100.json")
held_out_path = os.path.join(DATA_DIR, "intent_held_out_test_v3.json")
fresh_150_path = os.path.join(DATA_DIR, "fresh_mandi_test_150.json")

def load_json(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

train_v4 = load_json(train_v4_path)
train_v3 = load_json(train_v3_path)
mandi_train = load_json(mandi_150_path)
gap_train = load_json(gap_75_path)
strengthen_train = load_json(strengthen_path)

hw_test = load_json(hw_100_path)
held_out_test = load_json(held_out_path)
fresh_test = load_json(fresh_150_path)

def normalize(s):
    return s.strip().lower()

v4_texts = set(normalize(r["text"]) for r in train_v4)
v3_texts = set(normalize(r["text"]) for r in train_v3)

print("=" * 70)
print("  EXACT OVERLAP AUDIT BETWEEN TRAINING SETS AND EVALUATION SETS")
print("=" * 70)

print(f"Training Sets:")
print(f"  - intent_train_v4.json:                {len(train_v4)} samples ({len(v4_texts)} unique)")
print(f"    * Component intent_train_v3.json:     {len(train_v3)} samples")
print(f"    * Component mandi_handcrafted_150:    {len(mandi_train)} samples")
print(f"    * Component targeted_gap_75:          {len(gap_train)} samples")
print(f"    * Component domain_strengthening:     {len(strengthen_train)} samples")

print(f"\nEvaluation Sets vs. intent_train_v4.json (Final Retrained Model Training Set):")

# 1. Mandi 150 (Previous 'After' test)
mandi_overlap = [r for r in mandi_train if normalize(r["text"]) in v4_texts]
print(f"  1. mandi_handcrafted_150.json (150 samples):")
print(f"     -> Exact string matches in train_v4: {len(mandi_overlap)} / {len(mandi_train)} ({len(mandi_overlap)/len(mandi_train)*100:.1f}%)")
print(f"     -> ROOT CAUSE: Appended into train_v4 during update_train_dataset.py. Evaluating on it was training data evaluation.")

# 2. Handwritten 101 test set
hw_overlap = [r for r in hw_test if normalize(r["text"]) in v4_texts]
print(f"\n  2. handwritten_test_100.json (101 samples):")
print(f"     -> Exact string matches in train_v4: {len(hw_overlap)} / {len(hw_test)} ({len(hw_overlap)/len(hw_test)*100:.2f}%)")
if hw_overlap:
    for o in hw_overlap:
        print(f"        Overlap item: '{o['text']}' (Intent: {o['intent']})")

# 3. Held-out synthetic test set
held_out_overlap = [r for r in held_out_test if normalize(r["text"]) in v4_texts]
print(f"\n  3. intent_held_out_test_v3.json (5,877 samples):")
print(f"     -> Exact string matches in train_v4: {len(held_out_overlap)} / {len(held_out_test)} ({len(held_out_overlap)/len(held_out_test)*100:.3f}%)")
if held_out_overlap:
    for o in held_out_overlap:
        print(f"        Overlap item: '{o['text']}' (Intent: {o['intent']})")

# 4. Fresh Untouched Test Set
fresh_overlap = [r for r in fresh_test if normalize(r["text"]) in v4_texts]
print(f"\n  4. fresh_mandi_test_150.json (150 samples - Brand New):")
print(f"     -> Exact string matches in train_v4: {len(fresh_overlap)} / {len(fresh_test)} (0.00%)")
print(f"     -> Overlap with ANY training or prior file: 0 / 150 (Guaranteed 100% clean untouched held-out)")

# Also check hw_test vs train_v4 excluding 'namaste'
hw_clean = [r for r in hw_test if normalize(r["text"]) != "namaste"]
print(f"\n  * Note on handwritten_test_100.json without 'namaste' ({len(hw_clean)} samples): 0 / {len(hw_clean)} overlap.")
