import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Inventory, ForecastDemand, PurchaseOrder, ProductionPlan
)
from backend.app.services.inventory_engine import calculate_projected_inventory

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def setup_test_master(db):
    sku = SKU(sku_id="SKU-TEST-01", sku_name="Test SKU", category="Test", unit_of_measure="PCS", unit_cost=10.0, criticality="High", is_active=True)
    loc = Location(location_id="LOC-TEST-01", location_name="Test Loc", location_type="Warehouse", region="North", storage_capacity=10000.0)
    db.add(sku)
    db.add(loc)
    db.commit()

def test_1_opening_inventory_no_demand(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=100.0, reserved_quantity=10.0, safety_stock=20.0)
    test_db.add(inv)
    test_db.commit()

    res = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res["opening_available"] == 90.0 # 100 - 10
    assert res["projected_available"] == 90.0

def test_2_demand_reducing_inventory_consecutive_weeks(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=100.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=30.0)
    d2 = ForecastDemand(demand_id="DEM-2", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W02", forecast_quantity=40.0)
    test_db.add(d1)
    test_db.add(d2)
    test_db.commit()

    res_w1 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res_w1["projected_available"] == 70.0 # 100 - 30

    res_w2 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W02")
    assert res_w2["opening_available"] == 70.0 # Carried over from week 1 closing
    assert res_w2["projected_available"] == 30.0 # 70 - 40

def test_3_4_5_po_arrival_week_2(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    d2 = ForecastDemand(demand_id="DEM-2", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W02", forecast_quantity=20.0)
    po = PurchaseOrder(po_id="PO-1", supplier_id="SUP-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=100.0, received_quantity=100.0, expected_delivery_date="2026-W02", status="Pending", is_duplicate=False)
    test_db.add(d1)
    test_db.add(d2)
    test_db.add(po)
    test_db.commit()

    # Week 1 should NOT include PO arriving in week 2
    res_w1 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res_w1["inbound_receipts"] == 0.0
    assert res_w1["projected_available"] == 30.0 # 50 - 20

    # Week 2 SHOULD include PO arriving in week 2 exactly once
    res_w2 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W02")
    assert res_w2["opening_available"] == 30.0
    assert res_w2["inbound_receipts"] == 100.0
    assert res_w2["projected_available"] == 110.0 # 30 + 100 - 20

def test_6_cancelled_po_excluded(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    po = PurchaseOrder(po_id="PO-1", supplier_id="SUP-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=100.0, received_quantity=0.0, expected_delivery_date="2026-W01", status="Cancelled", is_duplicate=False)
    test_db.add(d1)
    test_db.add(po)
    test_db.commit()

    res = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res["inbound_receipts"] == 0.0

def test_7_already_received_stock(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=150.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    po = PurchaseOrder(po_id="PO-1", supplier_id="SUP-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=100.0, received_quantity=100.0, expected_delivery_date="2026-W01", status="Received", is_duplicate=False)
    test_db.add(d1)
    test_db.add(po)
    test_db.commit()

    res = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    # If received stock is already in on_hand, we query status == Received and sum received_quantity.
    assert res["inbound_receipts"] == 100.0

def test_8_production_output_completion(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    d2 = ForecastDemand(demand_id="DEM-2", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W02", forecast_quantity=20.0)
    prod = ProductionPlan(production_id="PROD-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", planned_quantity=500.0, production_start="2026-W01", production_end="2026-W02", capacity_available=1000.0, status="Planned")
    test_db.add(d1)
    test_db.add(d2)
    test_db.add(prod)
    test_db.commit()

    res_w1 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res_w1["production_receipts"] == 500.0 # per current matching rule (matches start or end)

def test_9_duplicate_inbound_records_excluded(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    po1 = PurchaseOrder(po_id="PO-1", supplier_id="SUP-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=100.0, received_quantity=100.0, expected_delivery_date="2026-W01", status="Pending", is_duplicate=False)
    po2 = PurchaseOrder(po_id="PO-1-DUP", supplier_id="SUP-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=100.0, received_quantity=100.0, expected_delivery_date="2026-W01", status="Pending", is_duplicate=True)
    test_db.add(d1)
    test_db.add(po1)
    test_db.add(po2)
    test_db.commit()

    res = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res["inbound_receipts"] == 100.0 # Only po1 counted, duplicate excluded

def test_10_multiple_pos_same_week(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    po1 = PurchaseOrder(po_id="PO-1", supplier_id="SUP-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=100.0, received_quantity=100.0, expected_delivery_date="2026-W01", status="Pending", is_duplicate=False)
    po2 = PurchaseOrder(po_id="PO-2", supplier_id="SUP-2", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", ordered_quantity=200.0, received_quantity=200.0, expected_delivery_date="2026-W01", status="Pending", is_duplicate=False)
    test_db.add(d1)
    test_db.add(po1)
    test_db.add(po2)
    test_db.commit()

    res = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res["inbound_receipts"] == 300.0

def test_11_demand_exceeding_inventory(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=10.0, reserved_quantity=0.0, safety_stock=5.0)
    test_db.add(inv)

    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=50.0)
    test_db.add(d1)
    test_db.commit()

    res = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res["projected_available"] == -40.0 # 10 - 50

def test_12_13_idempotency_and_determinism(test_db):
    setup_test_master(test_db)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", on_hand_quantity=50.0, reserved_quantity=0.0, safety_stock=10.0)
    test_db.add(inv)
    d1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-TEST-01", location_id="LOC-TEST-01", week_start="2026-W01", forecast_quantity=20.0)
    test_db.add(d1)
    test_db.commit()

    res1 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    res2 = calculate_projected_inventory(test_db, "SKU-TEST-01", "LOC-TEST-01", "2026-W01")
    assert res1 == res2

def test_14_sku_location_boundaries(test_db):
    sku1 = SKU(sku_id="SKU-1", sku_name="S1", category="C", unit_of_measure="PCS", unit_cost=10, criticality="High", is_active=True)
    sku2 = SKU(sku_id="SKU-2", sku_name="S2", category="C", unit_of_measure="PCS", unit_cost=10, criticality="High", is_active=True)
    loc1 = Location(location_id="LOC-1", location_name="L1", location_type="Warehouse", region="R", storage_capacity=1000)
    loc2 = Location(location_id="LOC-2", location_name="L2", location_type="Warehouse", region="R", storage_capacity=1000)
    test_db.add_all([sku1, sku2, loc1, loc2])

    inv1 = Inventory(inventory_id="INV-1", sku_id="SKU-1", location_id="LOC-1", on_hand_quantity=100, reserved_quantity=0, safety_stock=10)
    inv2 = Inventory(inventory_id="INV-2", sku_id="SKU-2", location_id="LOC-2", on_hand_quantity=200, reserved_quantity=0, safety_stock=10)
    test_db.add_all([inv1, inv2])

    d1 = ForecastDemand(demand_id="D1", sku_id="SKU-1", location_id="LOC-1", week_start="2026-W01", forecast_quantity=30)
    d2 = ForecastDemand(demand_id="D2", sku_id="SKU-2", location_id="LOC-2", week_start="2026-W01", forecast_quantity=50)
    test_db.add_all([d1, d2])
    test_db.commit()

    res1 = calculate_projected_inventory(test_db, "SKU-1", "LOC-1", "2026-W01")
    res2 = calculate_projected_inventory(test_db, "SKU-2", "LOC-2", "2026-W01")
    assert res1["projected_available"] == 70.0
    assert res2["projected_available"] == 150.0
