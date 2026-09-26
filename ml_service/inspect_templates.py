import sys
import re
import json
import pandas as pd
from sqlalchemy import create_engine

sys.stdout.reconfigure(encoding='utf-8')

engine = create_engine('oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl')
df = pd.read_sql("SELECT question, formula, solution, topic, difficulty FROM math_training_data", engine)

def mask_template(q):
    if not isinstance(q, str):
        return ""
    t = re.sub(r'\d+(\.\d+)?', '<N>', q)
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t

df['template'] = df['question'].apply(mask_template)
template_counts = df['template'].value_counts()

print(f"Total rows: {len(df)}")
print(f"Total template clusters: {len(template_counts)}")

templates_info = []
for i, (tmpl, cnt) in enumerate(template_counts.items(), 1):
    sample = df[df['template'] == tmpl].iloc[0]
    print(f"{i:2d}. [{cnt:5d}] ({sample['topic']:15s} | {sample['difficulty']:6s}) {tmpl}")
    templates_info.append({
        "id": i,
        "template": tmpl,
        "count": int(cnt),
        "topic": sample['topic'],
        "difficulty": sample['difficulty'],
        "sample_question": sample['question'],
        "sample_solution": sample['solution']
    })

with open("templates_breakdown.json", "w", encoding="utf-8") as f:
    json.dump(templates_info, f, indent=2)
