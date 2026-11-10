import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import SKU, Location, Supplier, ForecastDemand, PurchaseOrder
from backend.app.services.data_generator import generate_synthetic_data
import backend.app.services.data_generator as dg

@pytest.fixture
def temp_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine

def test_seed_determinism(temp_db_engine, monkeypatch):
    Session = sessionmaker(bind=temp_db_engine)
    monkeypatch.setattr(dg, "SessionLocal", Session)
    monkeypatch.setattr(dg, "engine", temp_db_engine)

    generate_synthetic_data(num_skus=5, num_locations=2, num_weeks=2, num_suppliers=2, num_pos=5, seed=123, reset=True)
    db = Session()
    skus_run1 = {s.sku_id: s.unit_cost for s in db.query(SKU).all()}
    demands_run1 = {d.demand_id: d.forecast_quantity for d in db.query(ForecastDemand).all()}
    db.close()

    Base.metadata.drop_all(bind=temp_db_engine)
    Base.metadata.create_all(bind=temp_db_engine)
    generate_synthetic_data(num_skus=5, num_locations=2, num_weeks=2, num_suppliers=2, num_pos=5, seed=123, reset=True)
    db = Session()
    skus_run2 = {s.sku_id: s.unit_cost for s in db.query(SKU).all()}
    demands_run2 = {d.demand_id: d.forecast_quantity for d in db.query(ForecastDemand).all()}
    db.close()

    assert skus_run1 == skus_run2
    assert demands_run1 == demands_run2

def test_seed_variation(temp_db_engine, monkeypatch):
    Session = sessionmaker(bind=temp_db_engine)
    monkeypatch.setattr(dg, "SessionLocal", Session)
    monkeypatch.setattr(dg, "engine", temp_db_engine)

    generate_synthetic_data(num_skus=5, num_locations=2, num_weeks=2, num_suppliers=2, num_pos=5, seed=111, reset=True)
    db = Session()
    costs_1 = [s.unit_cost for s in db.query(SKU).all()]
    db.close()

    Base.metadata.drop_all(bind=temp_db_engine)
    Base.metadata.create_all(bind=temp_db_engine)
    generate_synthetic_data(num_skus=5, num_locations=2, num_weeks=2, num_suppliers=2, num_pos=5, seed=999, reset=True)
    db = Session()
    costs_2 = [s.unit_cost for s in db.query(SKU).all()]
    db.close()

    assert costs_1 != costs_2

def test_non_destructive_behavior(temp_db_engine, monkeypatch):
    Session = sessionmaker(bind=temp_db_engine)
    monkeypatch.setattr(dg, "SessionLocal", Session)
    monkeypatch.setattr(dg, "engine", temp_db_engine)

    db = Session()
    dummy = SKU(sku_id="SKU-KEEP", sku_name="Keep Me", category="Test", unit_of_measure="PCS", unit_cost=10.0, criticality="Low", is_active=True)
    db.add(dummy)
    db.commit()
    db.close()

    generate_synthetic_data(num_skus=3, num_locations=2, num_weeks=2, num_suppliers=2, num_pos=2, seed=42, reset=False)

    db = Session()
    kept = db.query(SKU).filter_by(sku_id="SKU-KEEP").first()
    db.close()
    assert kept is not None
    assert kept.sku_name == "Keep Me"

def test_configurable_parameters(temp_db_engine, monkeypatch):
    Session = sessionmaker(bind=temp_db_engine)
    monkeypatch.setattr(dg, "SessionLocal", Session)
    monkeypatch.setattr(dg, "engine", temp_db_engine)

    generate_synthetic_data(num_skus=7, num_locations=3, num_weeks=4, num_suppliers=4, num_pos=10, seed=42, reset=True)
    db = Session()
    sku_count = db.query(SKU).count()
    loc_count = db.query(Location).count()
    sup_count = db.query(Supplier).count()
    po_count = db.query(PurchaseOrder).count() # num_pos (10) + 1 duplicate PO anomaly = 11
    db.close()

    assert sku_count == 7
    assert loc_count == 3
    assert sup_count == 4
    assert po_count == 11
