import pytest
import sqlite3
import os
from backend.app.database import run_database_migrations

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_migration.db"
    return str(db_file)

def test_migration_old_schema_missing_both(tmp_path):
    db_path = str(tmp_path / "old_both.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE mitigation_options (
            mitigation_id TEXT PRIMARY KEY,
            shortage_id TEXT,
            mitigation_type TEXT,
            proposed_quantity REAL,
            estimated_cost REAL,
            expected_arrival_date TEXT,
            feasibility_status TEXT,
            recommendation_score REAL,
            service_impact TEXT,
            is_approved BOOLEAN
        );
    """)
    cursor.execute("""
        INSERT INTO mitigation_options VALUES (
            'MIT-01', 'SHORT-01', 'SupplierPO', 100.0, 500.0, '2026-W12', 'Feasible', 90.0, 'High', 0
        );
    """)
    conn.commit()
    conn.close()

    run_database_migrations(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mitigation_options);")
    cols = [col[1] for col in cursor.fetchall()]
    assert "supplier_id" in cols
    assert "feasibility_explanation" in cols

    cursor.execute("SELECT mitigation_id, proposed_quantity FROM mitigation_options;")
    row = cursor.fetchone()
    assert row[0] == 'MIT-01'
    assert row[1] == 100.0
    conn.close()

def test_migration_missing_supplier_id_only(tmp_path):
    db_path = str(tmp_path / "old_sup.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE mitigation_options (
            mitigation_id TEXT PRIMARY KEY,
            feasibility_explanation TEXT,
            feasibility_status TEXT,
            is_approved BOOLEAN
        );
    """)
    cursor.execute("INSERT INTO mitigation_options VALUES ('MIT-02', 'Exp text', 'Feasible', 0);")
    conn.commit()
    conn.close()

    run_database_migrations(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mitigation_options);")
    cols = [col[1] for col in cursor.fetchall()]
    assert "supplier_id" in cols
    assert "feasibility_explanation" in cols
    conn.close()

def test_migration_missing_feasibility_explanation_only(tmp_path):
    db_path = str(tmp_path / "old_exp.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE mitigation_options (
            mitigation_id TEXT PRIMARY KEY,
            supplier_id TEXT,
            feasibility_status TEXT,
            is_approved BOOLEAN
        );
    """)
    cursor.execute("INSERT INTO mitigation_options VALUES ('MIT-03', 'SUP-01', 'Feasible', 0);")
    conn.commit()
    conn.close()

    run_database_migrations(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mitigation_options);")
    cols = [col[1] for col in cursor.fetchall()]
    assert "supplier_id" in cols
    assert "feasibility_explanation" in cols
    conn.close()

def test_migration_already_updated_schema(tmp_path):
    db_path = str(tmp_path / "updated.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE mitigation_options (
            mitigation_id TEXT PRIMARY KEY,
            supplier_id TEXT,
            feasibility_explanation TEXT,
            feasibility_status TEXT,
            is_approved BOOLEAN
        );
    """)
    conn.commit()
    conn.close()

    run_database_migrations(db_path)
    run_database_migrations(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mitigation_options);")
    cols = [col[1] for col in cursor.fetchall()]
    assert cols.count("supplier_id") == 1
    assert cols.count("feasibility_explanation") == 1
    conn.close()

def test_fresh_database_initialization(tmp_path):
    db_path = str(tmp_path / "fresh.db")
    run_database_migrations(db_path)
    assert os.path.exists(db_path)
