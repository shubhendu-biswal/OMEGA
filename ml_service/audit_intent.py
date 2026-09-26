import os
import sys
import json
import re
from collections import Counter
from sqlalchemy import create_engine, text
import pandas as pd

ORACLE_CONN_STR = "oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl"

def audit_intent():
    print("Connecting to Oracle DB...")
    engine = create_engine(ORACLE_CONN_STR)
    
    with engine.connect() as conn:
        print("Reading INTENT_TRAINING_DATA...")
        df = pd.read_sql(text("SELECT * FROM INTENT_TRAINING_DATA"), conn)
        print(f"Total rows in INTENT_TRAINING_DATA: {len(df):,}")
        print("Columns:", list(df.columns))
        print("Sample 5 rows:")
        print(df.head(5))
        
        # Check text and label column names
        cols = [c.upper() for c in df.columns]
        text_col = None
        label_col = None
        for c in df.columns:
            cu = c.upper()
            if cu in ['QUERY', 'QUESTION', 'TEXT', 'INPUT_TEXT', 'UTTERANCE', 'PROMPT']:
                text_col = c
            if cu in ['INTENT', 'LABEL', 'CATEGORY', 'INTENT_LABEL', 'CLASS']:
                label_col = c
                
        if not text_col or not label_col:
            # Fallback
            text_col = df.columns[0]
            label_col = df.columns[1]
            
        print(f"\nUsing Text Column: '{text_col}', Label Column: '{label_col}'")
        
        # Missing values
        print(f"Missing text count: {df[text_col].isna().sum()}")
        print(f"Missing label count: {df[label_col].isna().sum()}")
        df = df.dropna(subset=[text_col, label_col])
        
        # Clean whitespaces
        df['text_clean'] = df[text_col].astype(str).str.strip()
        df['label_clean'] = df[label_col].astype(str).str.strip().str.lower()
        
        # Duplicates
        total_rows = len(df)
        unique_texts = df['text_clean'].nunique()
        dup_texts = total_rows - unique_texts
        print(f"Unique texts: {unique_texts:,}, Duplicates: {dup_texts:,}")
        
        # Label counts
        label_counts = df['label_clean'].value_counts()
        print(f"\nTotal distinct labels: {len(label_counts)}")
        print("\nTop 25 labels and counts:")
        for label, count in label_counts.head(25).items():
            print(f"  - {label}: {count:,}")
            
        labels_under_50 = label_counts[label_counts < 50]
        print(f"\nLabels with count < 50: {len(labels_under_50)} labels")
        for label, count in labels_under_50.items():
            print(f"  - {label}: {count}")
            
        # Check other tables in database
        print("\nChecking CONVERSATION_TRAINING_DATA, DIALOG_TRAINING_DATA, FEEDBACK_TRAINING_DATA...")
        for tbl in ['CONVERSATION_TRAINING_DATA', 'DIALOG_TRAINING_DATA', 'FEEDBACK_TRAINING_DATA']:
            try:
                res = conn.execute(text(f"SELECT count(*) FROM {tbl}")).scalar()
                col_res = conn.execute(text(f"SELECT column_name FROM user_tab_cols WHERE table_name = '{tbl}'")).fetchall()
                cols = [r[0] for r in col_res]
                print(f"Table {tbl}: {res:,} rows, Columns: {cols}")
            except Exception as e:
                print(f"Could not inspect {tbl}: {e}")

if __name__ == "__main__":
    audit_intent()
