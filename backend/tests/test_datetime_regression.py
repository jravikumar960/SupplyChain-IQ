import pytest
import time
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import AuditLog, SimulationRun
from backend.app.services.simulation_engine import run_simulation
from backend.app.services.inventory_engine import date_to_week_str

def test_utc_timestamp_creation():
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    assert isinstance(now_utc, datetime)

def test_date_serialization_and_week_conversion():
    date_str = "2026-01-05"
    week_str = date_to_week_str(date_str)
    assert week_str == "2026-W02"

def test_naive_vs_aware_datetime_boundary():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    naive_dt = datetime.now(timezone.utc).replace(tzinfo=None)
    unique_id = f"AUDIT-TEST-{time.time_ns()}"
    log = AuditLog(
        audit_id=unique_id,
        entity_type="Test",
        entity_id="1",
        new_state="Active",
        event_type="CREATE",
        timestamp=naive_dt,
        explanation="Testing datetime boundary persistence"
    )
    db.add(log)
    db.commit()

    retrieved = db.query(AuditLog).filter(AuditLog.audit_id == unique_id).first()
    assert retrieved is not None
    assert isinstance(retrieved.timestamp, datetime)
    db.close()

def test_simulation_lead_time_and_history_retrieval():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    run = run_simulation(
        db,
        run_name="Datetime Regression Test",
        demand_multiplier=1.1,
        supplier_capacity_multiplier=0.9,
        lead_time_delay_days=14
    )
    assert run is not None
    assert run.simulation_id.startswith("SIM-")

    history = db.query(SimulationRun).filter(SimulationRun.simulation_id == run.simulation_id).first()
    assert history is not None
    assert history.run_name == "Datetime Regression Test"
    assert isinstance(history.created_at, datetime)
    db.close()
