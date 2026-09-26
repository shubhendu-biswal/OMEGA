from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("oracle+oracledb://OMEGA_user:omega123@localhost:1521/?service_name=orcl")

with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM INTENT_TRAINING_DATA"), conn)
    print("Label samples:")
    for label, group in df.groupby('intent'):
        print(f"\n--- LABEL: {label} (Total: {len(group)}) ---")
        samples = group['utterance'].head(3).tolist()
        for s in samples:
            print(f"  * {s}")
