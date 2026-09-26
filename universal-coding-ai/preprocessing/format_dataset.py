import json
import os

def format_instruction_dataset(input_file="dataset/cleaned/validated_dataset.json", output_file="dataset/processed/instruction_dataset.json"):
    if not os.path.exists(input_file):
        input_file = "dataset/cleaned/cleaned_dataset.json"

    with open(input_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    instruction_data = []

    for item in records:
        lang = item.get("programming_language", "Python")
        prob = item.get("problem_statement", "")
        input_spec = item.get("input", "")
        output_spec = item.get("output", "")
        constraints = item.get("constraints", "")
        examples = item.get("examples", "")

        user_content = f"Solve the following programming problem in {lang}:\n\n{prob}"
        if constraints:
            user_content += f"\n\nConstraints:\n{constraints}"
        if examples:
            user_content += f"\n\nExamples:\n{examples}"

        approach = item.get("approach", "Analyze the problem and identify optimal dynamic programming / hash table data structure strategy.")
        algorithm = item.get("algorithm", "Standard Optimal Execution Algorithm")
        code = item.get("solution", "")
        tc = item.get("time_complexity", "O(N)")
        sc = item.get("space_complexity", "O(1)")

        assistant_content = f"## Approach\n{approach}\n\n## Algorithm\n{algorithm}\n\n## Code\n```{lang.lower()}\n{code}\n```\n\n## Complexity\n- Time Complexity: {tc}\n- Space Complexity: {sc}"

        instruction_data.append({
            "id": item.get("id"),
            "language": lang,
            "category": item.get("category"),
            "messages": [
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ]
        })

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(instruction_data, f, indent=2)

    print(f"Formatted {len(instruction_data)} instruction tuning records -> {output_file}")

if __name__ == "__main__":
    format_instruction_dataset()
