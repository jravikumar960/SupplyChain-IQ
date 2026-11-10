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
    (such as supplier_id and feasibility_explanation on mitigation_options)
    without dropping, resetting, or overwriting existing records.
    """
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Check if table mitigation_options exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mitigation_options';")
        table_exists = cursor.fetchone()

        if table_exists:
            cursor.execute("PRAGMA table_info(mitigation_options);")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Idempotently add feasibility_explanation if missing
            if "feasibility_explanation" not in column_names:
                cursor.execute("ALTER TABLE mitigation_options ADD COLUMN feasibility_explanation TEXT;")
                conn.commit()

            # Idempotently add supplier_id if missing
            if "supplier_id" not in column_names:
                cursor.execute("ALTER TABLE mitigation_options ADD COLUMN supplier_id TEXT;")
                conn.commit()
    finally:
        conn.close()
