import os
import re
from collections import Counter
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine('oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl')

with engine.connect() as conn:
    cols = conn.execute(text("SELECT column_name, data_type, data_length FROM user_tab_cols WHERE table_name = 'MATH_TRAINING_DATA'")).fetchall()
    print("Columns:", cols)
    
    df = pd.read_sql("SELECT * FROM math_training_data", conn)
    print(f"Total rows loaded: {len(df)}")
    print("Columns in df:", df.columns.tolist())

# Unique questions & duplicates
total_rows = len(df)
unique_questions = df['QUESTION'].nunique() if 'QUESTION' in df.columns else df['question'].nunique()
col_q = 'QUESTION' if 'QUESTION' in df.columns else 'question'
col_ans = 'SOLUTION' if 'SOLUTION' in df.columns else 'solution'

duplicates = total_rows - unique_questions
print(f"Total records: {total_rows}")
print(f"Unique questions: {unique_questions}")
print(f"Duplicate questions: {duplicates}")

# Mask digits as <N> to cluster templates
def mask_template(q):
    if not isinstance(q, str):
        return ""
    # Mask numbers/decimals
    t = re.sub(r'\d+(\.\d+)?', '<N>', q)
    # Normalize whitespace
    t = re.sub(r'\s+', ' ', t).strip().lower()
    return t

df['template'] = df[col_q].apply(mask_template)
unique_templates = df['template'].nunique()
print(f"Number of template clusters: {unique_templates}")

# Top 10 templates
top_templates = df['template'].value_counts().head(10)
print("\nTop 10 Templates:")
for tmpl, cnt in top_templates.items():
    print(f"  [{cnt}]: {tmpl}")

# 20 random rows
print("\n--- 20 Random Rows Audit ---")
sample_20 = df.sample(n=min(20, len(df)), random_state=42)
for i, (_, row) in enumerate(sample_20.iterrows(), 1):
    q = row[col_q]
    ans = row[col_ans]
    # Check if answer has step-by-step or final value
    has_step = bool(re.search(r'step\s*\d+|therefore|because|align|calculate|divide|multiply|compute', str(ans), re.I))
    print(f"[{i}] Question: {q}")
    print(f"    Solution: {ans}")
    print(f"    Type: {'Step-by-step working' if has_step else 'Final value / concise'}")
