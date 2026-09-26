import json

log_path = r"c:\Users\shubh\.gemini\antigravity-ide\brain\db61bcfd-655c-4a39-8579-b6fed87263cb\.system_generated\logs\transcript_full.jsonl"
with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("source") == "USER_EXPLICIT":
            content = data.get("content", "")
            if "150" in content or "fresh" in content.lower() or "overlap" in content.lower():
                print("="*60)
                print(f"STEP: {data.get('step_index')}")
                print(content)
