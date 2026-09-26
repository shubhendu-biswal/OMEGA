import json
import os
import random

def split_dataset(input_file="dataset/processed/instruction_dataset.json", seed=42):
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    random.seed(seed)
    random.shuffle(data)

    total = len(data)
    train_end = int(total * 0.80)
    val_end = int(total * 0.90)

    train_set = data[:train_end]
    val_set = data[train_end:val_end]
    test_set = data[val_end:]

    # Verify no problem statement leakage between train and val/test
    train_problems = {item["messages"][0]["content"].strip().lower() for item in train_set}
    val_leakage = [item for item in val_set if item["messages"][0]["content"].strip().lower() in train_problems]
    test_leakage = [item for item in test_set if item["messages"][0]["content"].strip().lower() in train_problems]

    if val_leakage or test_leakage:
        print(f"Warning: Leakage detected (Val: {len(val_leakage)}, Test: {len(test_leakage)}). Filtering...")
        val_set = [item for item in val_set if item["messages"][0]["content"].strip().lower() not in train_problems]
        test_set = [item for item in test_set if item["messages"][0]["content"].strip().lower() not in train_problems]

    os.makedirs("dataset/train", exist_ok=True)
    os.makedirs("dataset/validation", exist_ok=True)
    os.makedirs("dataset/test", exist_ok=True)

    with open("dataset/train/train.json", "w", encoding="utf-8") as f:
        json.dump(train_set, f, indent=2)

    with open("dataset/validation/validation.json", "w", encoding="utf-8") as f:
        json.dump(val_set, f, indent=2)

    with open("dataset/test/test.json", "w", encoding="utf-8") as f:
        json.dump(test_set, f, indent=2)

    print("=== DATASET SPLIT REPORT ===")
    print(f"Total Records: {total}")
    print(f"Train Records (80%): {len(train_set)}")
    print(f"Validation Records (10%): {len(val_set)}")
    print(f"Test Records (10%): {len(test_set)}")

if __name__ == "__main__":
    split_dataset()
