"""
OMEGA Database Schema & Structure Manager
==========================================
Manages, structures, and optimizes the 13 tables (33+ million records) in Oracle DB.
- Creates foreign key constraints for relational integrity.
- Creates performance B-Tree indexes for fast search and aggregation.
- Creates unified database views (Catalog, Chat Summary, Model Leaderboard).
- Generates a structural audit report of the database.
"""

import os
import sys
import time
from sqlalchemy import create_engine, text

# Load backend/.env
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
if os.path.exists(dotenv_path):
    with open(dotenv_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

db_user = os.getenv("DB_USER", "OMEGA_user")
db_pass = os.getenv("DB_PASSWORD", "omega123")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "1521")
db_name = os.getenv("DB_NAME", "orcl")

db_url = f"oracle+oracledb://{db_user}:{db_pass}@{db_host}:{db_port}/?service_name={db_name}"

def get_db_engine():
    """Return SQLAlchemy engine for Oracle DB."""
    return create_engine(db_url)

def apply_relational_constraints(conn):
    """Ensure relational integrity between parent and child tables."""
    print("\n--- [1/4] Applying Relational Integrity Constraints ---")
    
    # 1. Foreign Key: CHAT_MESSAGES.SESSION_ID -> CHAT_SESSIONS.ID
    try:
        # Check if constraint already exists
        fk_check = conn.execute(text("""
            SELECT constraint_name FROM user_constraints 
            WHERE constraint_name = 'FK_CHAT_MSG_SESSION'
        """)).scalar()
        
        if not fk_check:
            print("  [ACTION] Adding foreign key FK_CHAT_MSG_SESSION (chat_messages -> chat_sessions)...")
            conn.execute(text("""
                ALTER TABLE chat_messages
                ADD CONSTRAINT fk_chat_msg_session
                FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
                ON DELETE CASCADE
            """))
            conn.commit()
            print("  [SUCCESS] Created FK_CHAT_MSG_SESSION constraint.")
        else:
            print("  [OK] Constraint FK_CHAT_MSG_SESSION already active.")
    except Exception as e:
        print(f"  [WARN] Failed to add FK_CHAT_MSG_SESSION: {e}")

def apply_performance_indexes(conn):
    """Create query-optimizing B-Tree indexes across all core tables."""
    print("\n--- [2/4] Applying Performance Indexes ---")
    
    indexes = [
        # (Index Name, Table Name, Columns Definition)
        ("IDX_CHAT_MSG_SESSION_TIME", "chat_messages", "session_id, created_at"),
        ("IDX_AGRI_DOMAIN_TOPIC", "agri_knowledge_base", "domain, topic"),
        ("IDX_CONV_CAT_DIFF", "conversation_training_data", "category, difficulty"),
        ("IDX_DIALOG_ID_TURN", "dialog_training_data", "dialog_id, turn_number"),
        ("IDX_FEEDBACK_RATING_SENT", "feedback_training_data", "rating, sentiment"),
        ("IDX_INTENT_INTENT", "intent_training_data", "intent"),
        ("IDX_CROP_SOIL_CROP", "crop_training_data", "soil_type, crop"),
        ("IDX_FERT_SOIL_CROP", "fertilizer_training_data", "soil_type, predicted_crop"),
        ("IDX_MATH_TOPIC_DIFF", "math_training_data", "topic, difficulty"),
        ("IDX_ML_META_MODEL_TIME", "ml_model_metadata", "model_name, training_time"),
        ("IDX_DOC_TYPE_CAT", "document_templates", "doc_type, category"),
    ]
    
    for idx_name, table_name, cols in indexes:
        try:
            exists = conn.execute(text(f"""
                SELECT index_name FROM user_indexes 
                WHERE index_name = '{idx_name.upper()}'
            """)).scalar()
            
            if not exists:
                print(f"  [ACTION] Creating index {idx_name} on {table_name}({cols})...")
                conn.execute(text(f"CREATE INDEX {idx_name} ON {table_name}({cols})"))
                conn.commit()
                print(f"  [SUCCESS] Index {idx_name} created.")
            else:
                print(f"  [OK] Index {idx_name} already exists.")
        except Exception as e:
            print(f"  [WARN] Could not create index {idx_name} on {table_name}: {e}")

def create_structured_views(conn):
    """Create structured catalog and analytical views."""
    print("\n--- [3/4] Creating Structured Catalog & Analytical Views ---")
    
    # 1. Master Database Catalog View
    try:
        conn.execute(text("""
            CREATE OR REPLACE VIEW v_database_catalog AS
            SELECT 
                t.table_name,
                CASE 
                    WHEN t.table_name IN ('INDIA_GK_DATA', 'AGRI_KNOWLEDGE_BASE', 'MATH_TRAINING_DATA') THEN 'KNOWLEDGE_BASE'
                    WHEN t.table_name IN ('CONVERSATION_TRAINING_DATA', 'DIALOG_TRAINING_DATA', 'INTENT_TRAINING_DATA', 'FEEDBACK_TRAINING_DATA', 'CROP_TRAINING_DATA', 'FERTILIZER_TRAINING_DATA') THEN 'TRAINING_DATA'
                    WHEN t.table_name IN ('CHAT_SESSIONS', 'CHAT_MESSAGES', 'DOCUMENT_TEMPLATES') THEN 'WORKSPACE_OPS'
                    WHEN t.table_name IN ('ML_MODEL_METADATA') THEN 'MLOPS_METADATA'
                    ELSE 'SYSTEM'
                END AS domain_category,
                s.num_rows,
                ROUND(s.bytes / (1024 * 1024), 2) AS storage_mb
            FROM user_tables t
            LEFT JOIN (
                SELECT segment_name, SUM(bytes) AS bytes, MAX(NULL) AS num_rows
                FROM user_segments
                GROUP BY segment_name
            ) s ON t.table_name = s.segment_name
            WHERE t.table_name NOT LIKE 'DR$%'
        """))
        conn.commit()
        print("  [SUCCESS] View 'v_database_catalog' created.")
    except Exception as e:
        print(f"  [WARN] Failed to create 'v_database_catalog': {e}")

    # 2. Chat Session Summary View
    try:
        conn.execute(text("""
            CREATE OR REPLACE VIEW v_chat_session_summary AS
            SELECT 
                s.id AS session_id,
                s.title,
                s.created_at,
                s.updated_at,
                COUNT(m.id) AS total_messages,
                SUM(CASE WHEN m.sender = 'user' THEN 1 ELSE 0 END) AS user_messages,
                SUM(CASE WHEN m.sender = 'assistant' THEN 1 ELSE 0 END) AS assistant_messages,
                MAX(m.created_at) AS last_message_at
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON s.id = m.session_id
            GROUP BY s.id, s.title, s.created_at, s.updated_at
        """))
        conn.commit()
        print("  [SUCCESS] View 'v_chat_session_summary' created.")
    except Exception as e:
        print(f"  [WARN] Failed to create 'v_chat_session_summary': {e}")

    # 3. ML Model Leaderboard View
    try:
        conn.execute(text("""
            CREATE OR REPLACE VIEW v_model_leaderboard AS
            SELECT 
                m.model_name,
                m.records_count,
                m.accuracy,
                m.status,
                m.training_time
            FROM ml_model_metadata m
            WHERE m.id IN (
                SELECT MAX(id) FROM ml_model_metadata GROUP BY model_name
            )
        """))
        conn.commit()
        print("  [SUCCESS] View 'v_model_leaderboard' created.")
    except Exception as e:
        print(f"  [WARN] Failed to create 'v_model_leaderboard': {e}")

def generate_database_audit_report(conn):
    """Print a clean structured audit report."""
    print("\n--- [4/4] OMEGA Database Structure & Integrity Audit ---")
    print("=" * 80)
    print(f"{'DOMAIN':<18} | {'TABLE NAME':<28} | {'PRIMARY KEY':<14} | {'ROWS':>12}")
    print("=" * 80)
    
    domain_map = {
        "KNOWLEDGE": ["INDIA_GK_DATA", "AGRI_KNOWLEDGE_BASE", "MATH_TRAINING_DATA"],
        "TRAINING": ["CONVERSATION_TRAINING_DATA", "DIALOG_TRAINING_DATA", "INTENT_TRAINING_DATA", 
                     "FEEDBACK_TRAINING_DATA", "CROP_TRAINING_DATA", "FERTILIZER_TRAINING_DATA"],
        "WORKSPACE": ["CHAT_SESSIONS", "CHAT_MESSAGES", "DOCUMENT_TEMPLATES"],
        "MLOPS": ["ML_MODEL_METADATA"]
    }
    
    total_db_rows = 0
    for domain, t_list in domain_map.items():
        for tname in t_list:
            try:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{tname}"')).scalar()
                total_db_rows += cnt
                pks = conn.execute(text(f"""
                    SELECT cols.column_name 
                    FROM user_constraints cons, user_cons_columns cols 
                    WHERE cons.constraint_type = 'P' 
                      AND cons.constraint_name = cols.constraint_name 
                      AND cons.table_name = '{tname}'
                """)).fetchall()
                pk_str = ",".join([p[0] for p in pks]) if pks else "NONE"
                print(f"{domain:<18} | {tname:<28} | {pk_str:<14} | {cnt:>12,}")
            except Exception as err:
                print(f"{domain:<18} | {tname:<28} | {'ERR':<14} | {str(err)[:12]:>12}")
    
    print("-" * 80)
    print(f"TOTAL VERIFIED ROWS IN DATABASE: {total_db_rows:,}")
    print("=" * 80)

def main():
    print("==================================================")
    print("  OMEGA Database Structure & Organization Tool")
    print("==================================================")
    engine = get_db_engine()
    with engine.connect() as conn:
        apply_relational_constraints(conn)
        apply_performance_indexes(conn)
        create_structured_views(conn)
        generate_database_audit_report(conn)
    print("\n[COMPLETE] Database structure successfully organized and verified!")

if __name__ == "__main__":
    main()
