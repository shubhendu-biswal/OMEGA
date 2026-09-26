import json
import os
import re

VALID_LANGUAGES = {
    "java": "Java", "python": "Python", "c": "C", "c++": "C++", "cpp": "C++",
    "javascript": "JavaScript", "js": "JavaScript", "typescript": "TypeScript", "ts": "TypeScript",
    "c#": "C#", "csharp": "C#", "go": "Go", "golang": "Go", "rust": "Rust",
    "kotlin": "Kotlin", "swift": "Swift", "php": "PHP", "ruby": "Ruby",
    "dart": "Dart", "scala": "Scala", "r": "R", "sql": "SQL", "matlab": "MATLAB"
}

def clean_text(text):
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def clean_dataset(input_file="dataset/raw/raw_dataset.json", output_file="dataset/cleaned/cleaned_dataset.json"):
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    total_records = len(records)
    valid_records = []
    removed_records = 0
    invalid_records = 0
    seen_problems = set()
    duplicate_records = 0

    for item in records:
        prob = clean_text(item.get("problem_statement", ""))
        code = clean_text(item.get("solution", ""))
        lang_raw = str(item.get("programming_language", "")).strip().lower()

        if not prob or not code or len(prob) < 10 or len(code) < 5:
            invalid_records += 1
            removed_records += 1
            continue

        if lang_raw not in VALID_LANGUAGES:
            invalid_records += 1
            removed_records += 1
            continue

        normalized_lang = VALID_LANGUAGES[lang_raw]

        # Duplicate check
        prob_key = prob.lower()[:100]
        if prob_key in seen_problems:
            duplicate_records += 1
            removed_records += 1
            continue

        seen_problems.add(prob_key)

        cleaned_item = {
            "id": item.get("id", f"REC-{len(valid_records)+1:03d}"),
            "problem_statement": prob,
            "input": clean_text(item.get("input", "")),
            "output": clean_text(item.get("output", "")),
            "constraints": clean_text(item.get("constraints", "")),
            "examples": clean_text(item.get("examples", "")),
            "programming_language": normalized_lang,
            "category": item.get("category", "General"),
            "difficulty": item.get("difficulty", "Medium"),
            "solution": code,
            "approach": clean_text(item.get("approach", "")),
            "algorithm": clean_text(item.get("algorithm", "")),
            "time_complexity": clean_text(item.get("time_complexity", "O(N)")),
            "space_complexity": clean_text(item.get("space_complexity", "O(1)"))
        }
        valid_records.append(cleaned_item)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2)

    report = {
        "total_records": total_records,
        "valid_records": len(valid_records),
        "removed_records": removed_records,
        "duplicate_records": duplicate_records,
        "invalid_records": invalid_records
    }

    report_path = "dataset/cleaned/cleaning_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("=== DATASET CLEANING REPORT ===")
    print(f"Total Records: {total_records}")
    print(f"Valid Records: {len(valid_records)}")
    print(f"Removed Records: {removed_records}")
    print(f"Duplicate Records: {duplicate_records}")
    print(f"Invalid Records: {invalid_records}")

if __name__ == "__main__":
    clean_dataset()
