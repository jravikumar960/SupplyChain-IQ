import pytest
import sqlite3
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from backend.app.database import run_database_migrations, DB_PATH

def test_lifespan_migration_with_old_schema(tmp_path, monkeypatch):
    # Use a temporary db path for testing lifespan startup migration
    temp_db_dir = tmp_path / "data"
    temp_db_dir.mkdir(exist_ok=True)
    temp_db_path = str(temp_db_dir / "supplychain_iq.db")

    # Monkeypatch DB_PATH in database module to use temp db
    import backend.app.database as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", temp_db_path)

    # 1. Setup an old-schema database missing supplier_id and feasibility_explanation
    conn = sqlite3.connect(temp_db_path)
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
            'MIT-LIFESPAN-01', 'SHORT-01', 'SupplierPO', 200.0, 1000.0, '2026-W12', 'Feasible', 95.0, 'High', 0
        );
    """)
    conn.commit()
    conn.close()

    # 2. Define a test FastAPI app using the same lifespan startup migration pattern
    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        run_database_migrations(temp_db_path)
        yield

    test_app = FastAPI(lifespan=test_lifespan)

    @test_app.get("/test-status")
    def test_status():
        return {"status": "ok"}

    # 3. Start TestClient (triggers lifespan startup event)
    with TestClient(test_app) as client:
        response = client.get("/test-status")
        assert response.status_code == 200

    # 4. Verify that the lifespan migration automatically added the missing columns and preserved records
    conn = sqlite3.connect(temp_db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mitigation_options);")
    cols = [col[1] for col in cursor.fetchall()]
    assert "supplier_id" in cols
    assert "feasibility_explanation" in cols

    cursor.execute("SELECT mitigation_id, proposed_quantity FROM mitigation_options;")
    row = cursor.fetchone()
    assert row[0] == 'MIT-LIFESPAN-01'
    assert row[1] == 200.0
    conn.close()

def test_lifespan_migration_fresh_database(tmp_path, monkeypatch):
    temp_db_dir = tmp_path / "data2"
    temp_db_dir.mkdir(exist_ok=True)
    temp_db_path = str(temp_db_dir / "supplychain_iq.db")

    @asynccontextmanager
    async def test_lifespan(app: FastAPI):
        run_database_migrations(temp_db_path)
        yield

    test_app = FastAPI(lifespan=test_lifespan)

    @test_app.get("/test-fresh")
    def test_fresh():
        return {"status": "fresh"}

    with TestClient(test_app) as client:
        response = client.get("/test-fresh")
        assert response.status_code == 200

    # Fresh database should have run migration without error
    assert os.path.exists(temp_db_path)
