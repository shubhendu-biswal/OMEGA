import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sandbox.executor import SandboxExecutor

def validate_dataset_code(input_file="dataset/cleaned/cleaned_dataset.json", output_file="dataset/cleaned/validated_dataset.json"):
    if not os.path.exists(input_file):
        print(f"File {input_file} does not exist.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    executor = SandboxExecutor(timeout_sec=5)
    validated = []
    failed_count = 0
    passed_count = 0

    for item in records:
        lang = item["programming_language"]
        code = item["solution"]

        res = executor.execute(lang, code)
        if res["success"]:
            passed_count += 1
            item["validated"] = True
            validated.append(item)
        else:
            failed_count += 1
            print(f"Validation failed for {item['id']} ({lang}): {res['stderr'][:100]}")
            # Keep item but mark validated False if non-fatal
            item["validated"] = False
            validated.append(item)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(validated, f, indent=2)

    print("=== CODE VALIDATION REPORT ===")
    print(f"Total Validated: {len(validated)}")
    print(f"Passed Execution: {passed_count}")
    print(f"Failed/Non-executable: {failed_count}")

if __name__ == "__main__":
    validate_dataset_code()
