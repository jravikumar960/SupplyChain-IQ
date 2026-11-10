import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "supplychain_iq.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def run_database_migrations(db_path: str = DB_PATH):
    """
    Safely and idempotently inspects the database schema and applies missing columns
    and tables without dropping, resetting, or overwriting existing records.
    """
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Check mitigation_options table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mitigation_options';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(mitigation_options);")
            col_names = [col[1] for col in cursor.fetchall()]
            if "feasibility_explanation" not in col_names:
                cursor.execute("ALTER TABLE mitigation_options ADD COLUMN feasibility_explanation TEXT;")
                conn.commit()
            if "supplier_id" not in col_names:
                cursor.execute("ALTER TABLE mitigation_options ADD COLUMN supplier_id TEXT;")
                conn.commit()

        # Check inventories table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventories';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(inventories);")
            col_names = [col[1] for col in cursor.fetchall()]
            if "unit_of_measure" not in col_names:
                cursor.execute("ALTER TABLE inventories ADD COLUMN unit_of_measure TEXT;")
                conn.commit()

        # Check purchase_orders table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='purchase_orders';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(purchase_orders);")
            col_names = [col[1] for col in cursor.fetchall()]
            if "unit_of_measure" not in col_names:
                cursor.execute("ALTER TABLE purchase_orders ADD COLUMN unit_of_measure TEXT;")
                conn.commit()

        # Check boms table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='boms';")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(boms);")
            col_names = [col[1] for col in cursor.fetchall()]
            if "component_unit_of_measure" not in col_names:
                cursor.execute("ALTER TABLE boms ADD COLUMN component_unit_of_measure TEXT;")
                conn.commit()

        # Ensure detector_executions table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detector_executions (
                execution_id TEXT PRIMARY KEY,
                evaluation_run_id TEXT NOT NULL,
                detector_type TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                executed_at DATETIME
            );
        """)
        conn.commit()
    finally:
        conn.close()
