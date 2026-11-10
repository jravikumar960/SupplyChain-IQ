import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Inventory, ForecastDemand, Shortage
)
from backend.app.services.shortage_engine import detect_and_save_shortages
from backend.app.services.prioritization_engine import calculate_priority_score

@pytest.fixture
def shortage_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def setup_master(db, sku_id="SKU-S-01", criticality="Critical", location_id="LOC-S-01"):
    sku = SKU(sku_id=sku_id, sku_name=f"SKU {sku_id}", category="Test", unit_of_measure="PCS", unit_cost=20.0, criticality=criticality, is_active=True)
    loc = Location(location_id=location_id, location_name=f"Loc {location_id}", location_type="Warehouse", region="North", storage_capacity=10000.0)
    db.merge(sku)
    db.merge(loc)
    db.commit()

def test_no_shortage(shortage_db):
    setup_master(shortage_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-S-01", location_id="LOC-S-01", on_hand_quantity=200.0, reserved_quantity=0.0, safety_stock=20.0)
    demand = ForecastDemand(demand_id="DEM-1", sku_id="SKU-S-01", location_id="LOC-S-01", week_start="2026-W01", forecast_quantity=50.0)
    shortage_db.add(inv)
    shortage_db.add(demand)
    shortage_db.commit()

    count = detect_and_save_shortages(shortage_db)
    assert count == 0
    assert shortage_db.query(Shortage).count() == 0

def test_shortage_low_severity(shortage_db):
    setup_master(shortage_db, sku_id="SKU-10", criticality="Low", location_id="LOC-10")
    inv1 = Inventory(inventory_id="INV-10", sku_id="SKU-10", location_id="LOC-10", on_hand_quantity=90.0, reserved_quantity=0.0, safety_stock=100.0)
    d1 = ForecastDemand(demand_id="D-10", sku_id="SKU-10", location_id="LOC-10", week_start="2026-W01", forecast_quantity=0.0)
    shortage_db.add_all([inv1, d1])
    shortage_db.commit()
    detect_and_save_shortages(shortage_db)
    assert shortage_db.query(Shortage).filter_by(sku_id="SKU-10").first().severity == "Low"

def test_shortage_medium_severity(shortage_db):
    setup_master(shortage_db, sku_id="SKU-500", criticality="Medium", location_id="LOC-500")
    inv2 = Inventory(inventory_id="INV-500", sku_id="SKU-500", location_id="LOC-500", on_hand_quantity=0.0, reserved_quantity=0.0, safety_stock=500.0)
    d2 = ForecastDemand(demand_id="D-500", sku_id="SKU-500", location_id="LOC-500", week_start="2026-W01", forecast_quantity=0.0)
    shortage_db.add_all([inv2, d2])
    shortage_db.commit()
    detect_and_save_shortages(shortage_db)
    assert shortage_db.query(Shortage).filter_by(sku_id="SKU-500").first().severity == "Medium"

def test_shortage_high_severity(shortage_db):
    setup_master(shortage_db, sku_id="SKU-501", criticality="Medium", location_id="LOC-501")
    inv3 = Inventory(inventory_id="INV-501", sku_id="SKU-501", location_id="LOC-501", on_hand_quantity=0.0, reserved_quantity=0.0, safety_stock=501.0)
    d3 = ForecastDemand(demand_id="D-501", sku_id="SKU-501", location_id="LOC-501", week_start="2026-W01", forecast_quantity=0.0)
    shortage_db.add_all([inv3, d3])
    shortage_db.commit()
    detect_and_save_shortages(shortage_db)
    assert shortage_db.query(Shortage).filter_by(sku_id="SKU-501").first().severity == "High"

def test_zero_safety_stock_no_shortage(shortage_db):
    setup_master(shortage_db, sku_id="SKU-ZERO", criticality="Medium", location_id="LOC-ZERO")
    inv4 = Inventory(inventory_id="INV-ZERO", sku_id="SKU-ZERO", location_id="LOC-ZERO", on_hand_quantity=0.0, reserved_quantity=0.0, safety_stock=0.0)
    d4 = ForecastDemand(demand_id="D-ZERO", sku_id="SKU-ZERO", location_id="LOC-ZERO", week_start="2026-W01", forecast_quantity=0.0)
    shortage_db.add_all([inv4, d4])
    shortage_db.commit()
    cnt = detect_and_save_shortages(shortage_db)
    assert cnt == 0

def test_negative_inventory_critical_severity(shortage_db):
    setup_master(shortage_db, sku_id="SKU-NEG", criticality="Critical", location_id="LOC-NEG")
    inv5 = Inventory(inventory_id="INV-NEG", sku_id="SKU-NEG", location_id="LOC-NEG", on_hand_quantity=10.0, reserved_quantity=0.0, safety_stock=100.0)
    d5 = ForecastDemand(demand_id="D-NEG", sku_id="SKU-NEG", location_id="LOC-NEG", week_start="2026-W01", forecast_quantity=50.0)
    shortage_db.add_all([inv5, d5])
    shortage_db.commit()
    detect_and_save_shortages(shortage_db)
    assert shortage_db.query(Shortage).filter_by(sku_id="SKU-NEG").first().severity == "Critical"

def test_critical_sku_fifty_percent_safety_high(shortage_db):
    setup_master(shortage_db, sku_id="SKU-CRIT-50", criticality="Critical", location_id="LOC-C50")
    inv6 = Inventory(inventory_id="INV-C50", sku_id="SKU-CRIT-50", location_id="LOC-C50", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=100.0)
    d6 = ForecastDemand(demand_id="D-C50", sku_id="SKU-CRIT-50", location_id="LOC-C50", week_start="2026-W01", forecast_quantity=0.0)
    shortage_db.add_all([inv6, d6])
    shortage_db.commit()
    detect_and_save_shortages(shortage_db)
    assert shortage_db.query(Shortage).filter_by(sku_id="SKU-CRIT-50").first().severity == "High"

def test_prioritization_all_categories_and_bounds():
    assert calculate_priority_score("Low", "Low", 0.0) == 10.0
    assert calculate_priority_score("Critical", "Critical", 3000.0) == 100.0
    assert calculate_priority_score("Medium", "High", 250.0) == 37.5

def test_equal_score_tie_breaking(shortage_db):
    setup_master(shortage_db, sku_id="SKU-B", criticality="Medium", location_id="LOC-S-01")
    skuA = SKU(sku_id="SKU-A", sku_name="SKU A", category="Test", unit_of_measure="PCS", unit_cost=10, criticality="Medium", is_active=True)
    loc1 = Location(location_id="LOC-1", location_name="L1", location_type="Warehouse", region="R", storage_capacity=1000)
    shortage_db.merge(skuA)
    shortage_db.merge(loc1)

    inv1 = Inventory(inventory_id="I1", sku_id="SKU-A", location_id="LOC-1", on_hand_quantity=10, reserved_quantity=0, safety_stock=50)
    inv2 = Inventory(inventory_id="I2", sku_id="SKU-B", location_id="LOC-S-01", on_hand_quantity=10, reserved_quantity=0, safety_stock=50)
    d1 = ForecastDemand(demand_id="DA", sku_id="SKU-A", location_id="LOC-1", week_start="2026-W01", forecast_quantity=0)
    d2 = ForecastDemand(demand_id="DB", sku_id="SKU-B", location_id="LOC-S-01", week_start="2026-W01", forecast_quantity=0)
    shortage_db.add_all([inv1, inv2, d1, d2])
    shortage_db.commit()

    detect_and_save_shortages(shortage_db)
    shortages = shortage_db.query(Shortage).all()
    assert len(shortages) == 2
    assert shortages[0].sku_id == "SKU-A"
    assert shortages[1].sku_id == "SKU-B"

def test_transaction_rollback_and_commit(shortage_db):
    setup_master(shortage_db, sku_id="SKU-TX", criticality="Critical", location_id="LOC-TX")
    inv = Inventory(inventory_id="INV-TX", sku_id="SKU-TX", location_id="LOC-TX", on_hand_quantity=10.0, reserved_quantity=0.0, safety_stock=20.0)
    demand = ForecastDemand(demand_id="DEM-TX", sku_id="SKU-TX", location_id="LOC-TX", week_start="2026-W01", forecast_quantity=50.0)
    shortage_db.add(inv)
    shortage_db.add(demand)
    shortage_db.commit()

    count = detect_and_save_shortages(shortage_db)
    assert count == 1
    assert shortage_db.query(Shortage).count() == 1

    try:
        with shortage_db.begin_nested():
            shortage_db.query(Shortage).delete()
            raise RuntimeError("Simulated failure during insert")
    except RuntimeError:
        shortage_db.rollback()

    assert shortage_db.query(Shortage).count() == 1
