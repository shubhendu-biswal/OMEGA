import json
import os
import random
from collections import Counter

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "data")

train_v3_path = os.path.join(DATA_DIR, "intent_train_v3.json")
mandi_path = os.path.join(DATA_DIR, "mandi_handcrafted_150.json")
gap_path = os.path.join(DATA_DIR, "targeted_gap_75.json")
strengthening_path = os.path.join(DATA_DIR, "domain_strengthening_train.json")

with open(train_v3_path, "r", encoding="utf-8") as f:
    train_data = json.load(f)

with open(mandi_path, "r", encoding="utf-8") as f:
    mandi_data = json.load(f)

with open(gap_path, "r", encoding="utf-8") as f:
    gap_data = json.load(f)

with open(strengthening_path, "r", encoding="utf-8") as f:
    strengthening_data = json.load(f)

print(f"Base train samples: {len(train_data)}")
print(f"Adding mandi samples: {len(mandi_data)}")
print(f"Adding gap samples: {len(gap_data)}")
print(f"Adding strengthening samples: {len(strengthening_data)}")

# Merge
train_v4 = train_data + mandi_data + gap_data + strengthening_data
random.seed(42)
random.shuffle(train_v4)

out_path = os.path.join(DATA_DIR, "intent_train_v4.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(train_v4, f, indent=2, ensure_ascii=False)

print(f"\nFinal Train v4 Samples: {len(train_v4)}")
print(f"Distribution: {Counter(r['intent'] for r in train_v4)}")
print(f"Saved to: {out_path}")
