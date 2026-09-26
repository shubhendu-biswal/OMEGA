import json
import os
import hashlib

def hash_text(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def remove_duplicates(input_file="dataset/cleaned/cleaned_dataset.json", output_file="dataset/cleaned/cleaned_dataset.json"):
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    seen_hashes = set()
    deduped = []
    removed_count = 0

    for item in data:
        key = hash_text(item["problem_statement"] + item["programming_language"])
        if key in seen_hashes:
            removed_count += 1
            continue
        seen_hashes.add(key)
        deduped.append(item)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2)

    print(f"Deduplication complete. Retained {len(deduped)} records, removed {removed_count} duplicates.")

if __name__ == "__main__":
    remove_duplicates()
