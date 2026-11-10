import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Inventory, PurchaseOrder, ForecastDemand, DataIssue
)
from backend.app.services.inventory_engine import calculate_projected_inventory
from backend.app.services.uom_engine import validate_uom_compatibility

@pytest.fixture
def uom_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_inventory_projection_uom_kg_to_ton(uom_db):
    sku = SKU(sku_id="SKU-KG1", sku_name="Material KG", category="Raw", unit_of_measure="KG", unit_cost=5.0, criticality="High", is_active=True)
    loc = Location(location_id="LOC-1", location_name="Warehouse 1", location_type="Warehouse", region="North", storage_capacity=10000.0)
    inv = Inventory(inventory_id="INV-1", sku_id="SKU-KG1", location_id="LOC-1", on_hand_quantity=500.0, reserved_quantity=0.0, safety_stock=100.0, unit_of_measure="KG")
    po = PurchaseOrder(po_id="PO-1", supplier_id="SUP-1", sku_id="SKU-KG1", location_id="LOC-1", ordered_quantity=2.0, received_quantity=2.0, expected_delivery_date="2026-W01", status="Received", unit_of_measure="TON")
    demand = ForecastDemand(demand_id="DEM-1", sku_id="SKU-KG1", location_id="LOC-1", week_start="2026-W01", forecast_quantity=1500.0)

    uom_db.add_all([sku, loc, inv, po, demand])
    uom_db.commit()

    res = calculate_projected_inventory(uom_db, "SKU-KG1", "LOC-1", "2026-W01")
    assert res["inbound_receipts"] == 2000.0
    assert res["projected_available"] == 1000.0

def test_inventory_projection_uom_box_to_pcs(uom_db):
    sku = SKU(sku_id="SKU-BOX1", sku_name="Parts Box", category="Parts", unit_of_measure="PCS", unit_cost=10.0, criticality="Medium", is_active=True)
    loc = Location(location_id="LOC-1", location_name="Warehouse 1", location_type="Warehouse", region="North", storage_capacity=10000.0)
    inv = Inventory(inventory_id="INV-BOX", sku_id="SKU-BOX1", location_id="LOC-1", on_hand_quantity=10.0, reserved_quantity=0.0, safety_stock=5.0, unit_of_measure="PCS")
    po = PurchaseOrder(po_id="PO-BOX", supplier_id="SUP-1", sku_id="SKU-BOX1", location_id="LOC-1", ordered_quantity=5.0, received_quantity=5.0, expected_delivery_date="2026-W01", status="Received", unit_of_measure="BOX")
    demand = ForecastDemand(demand_id="DEM-BOX", sku_id="SKU-BOX1", location_id="LOC-1", week_start="2026-W01", forecast_quantity=20.0)

    uom_db.add_all([sku, loc, inv, po, demand])
    uom_db.commit()

    res = calculate_projected_inventory(uom_db, "SKU-BOX1", "LOC-1", "2026-W01")
    assert res["inbound_receipts"] == 60.0
    assert res["projected_available"] == 50.0

def test_inventory_projection_missing_po_uom(uom_db):
    sku = SKU(sku_id="SKU-M1", sku_name="Missing PO UOM", category="Parts", unit_of_measure="PCS", unit_cost=10.0, criticality="High", is_active=True)
    loc = Location(location_id="LOC-1", location_name="Warehouse 1", location_type="Warehouse", region="North", storage_capacity=10000.0)
    inv = Inventory(inventory_id="INV-M1", sku_id="SKU-M1", location_id="LOC-1", on_hand_quantity=100.0, reserved_quantity=0.0, safety_stock=10.0, unit_of_measure="PCS")
    po = PurchaseOrder(po_id="PO-M1", supplier_id="SUP-1", sku_id="SKU-M1", location_id="LOC-1", ordered_quantity=50.0, received_quantity=50.0, expected_delivery_date="2026-W01", status="Received", unit_of_measure="")
    demand = ForecastDemand(demand_id="DEM-M1", sku_id="SKU-M1", location_id="LOC-1", week_start="2026-W01", forecast_quantity=10.0)

    uom_db.add_all([sku, loc, inv, po, demand])
    uom_db.commit()

    res = calculate_projected_inventory(uom_db, "SKU-M1", "LOC-1", "2026-W01")
    assert res["inbound_receipts"] == 0.0
    assert res["projected_available"] == 90.0
    issue = uom_db.query(DataIssue).filter_by(affected_entity_id="PO-M1").first()
    assert issue is not None
    assert "Missing PO unit of measure" in issue.detection_result

def test_inventory_projection_missing_canonical_uom(uom_db):
    sku = SKU(sku_id="SKU-M2", sku_name="Missing Canonical UOM", category="Parts", unit_of_measure="", unit_cost=10.0, criticality="High", is_active=True)
    loc = Location(location_id="LOC-1", location_name="Warehouse 1", location_type="Warehouse", region="North", storage_capacity=10000.0)
    inv = Inventory(inventory_id="INV-M2", sku_id="SKU-M2", location_id="LOC-1", on_hand_quantity=100.0, reserved_quantity=0.0, safety_stock=10.0, unit_of_measure="")
    po = PurchaseOrder(po_id="PO-M2", supplier_id="SUP-1", sku_id="SKU-M2", location_id="LOC-1", ordered_quantity=50.0, received_quantity=50.0, expected_delivery_date="2026-W01", status="Received", unit_of_measure="PCS")
    demand = ForecastDemand(demand_id="DEM-M2", sku_id="SKU-M2", location_id="LOC-M2", week_start="2026-W01", forecast_quantity=10.0)

    uom_db.add_all([sku, loc, inv, po, demand])
    uom_db.commit()

    res = calculate_projected_inventory(uom_db, "SKU-M2", "LOC-1", "2026-W01")
    assert res["inbound_receipts"] == 0.0
    issue = uom_db.query(DataIssue).filter_by(affected_entity_id="SKU-M2").first()
    assert issue is not None
    assert "Missing canonical inventory unit" in issue.detection_result

def test_inventory_projection_double_execution_purity_and_dedup(uom_db):
    sku = SKU(sku_id="SKU-DUP", sku_name="Dup Test", category="Parts", unit_of_measure="PCS", unit_cost=10.0, criticality="High", is_active=True)
    loc = Location(location_id="LOC-1", location_name="Warehouse 1", location_type="Warehouse", region="North", storage_capacity=10000.0)
    inv = Inventory(inventory_id="INV-DUP", sku_id="SKU-DUP", location_id="LOC-1", on_hand_quantity=100.0, reserved_quantity=0.0, safety_stock=10.0, unit_of_measure="PCS")
    po = PurchaseOrder(po_id="PO-DUP", supplier_id="SUP-1", sku_id="SKU-DUP", location_id="LOC-1", ordered_quantity=50.0, received_quantity=50.0, expected_delivery_date="2026-W01", status="Received", unit_of_measure="")
    demand = ForecastDemand(demand_id="DEM-DUP", sku_id="SKU-DUP", location_id="LOC-1", week_start="2026-W01", forecast_quantity=10.0)

    uom_db.add_all([sku, loc, inv, po, demand])
    uom_db.commit()

    # First execution
    res1 = calculate_projected_inventory(uom_db, "SKU-DUP", "LOC-1", "2026-W01")
    issues_count_1 = uom_db.query(DataIssue).filter_by(affected_entity_id="PO-DUP").count()

    # Second identical execution
    res2 = calculate_projected_inventory(uom_db, "SKU-DUP", "LOC-1", "2026-W01")
    issues_count_2 = uom_db.query(DataIssue).filter_by(affected_entity_id="PO-DUP").count()

    # Verify projection purity & idempotency
    assert res1 == res2
    assert issues_count_1 == 1
    assert issues_count_2 == 1  # No duplicate DataIssue records created

    # Verify unrelated operational inventory record remains unchanged
    inv_check = uom_db.query(Inventory).filter_by(inventory_id="INV-DUP").first()
    assert inv_check.on_hand_quantity == 100.0

def test_inventory_projection_invalid_factors_and_isolation():
    compat, _, _ = validate_uom_compatibility("BOX", "PCS", conversion_map={"BOX": {"PCS": 20.0}}, sku_id="SKU-A", target_sku_id="SKU-B")
    assert compat is False

    for bad_factor in [0.0, -1.5, float('nan'), float('inf')]:
        compat, _, _ = validate_uom_compatibility("BOX", "PCS", conversion_map={"BOX": {"PCS": bad_factor}})
        assert compat is False

    compat, _, factor = validate_uom_compatibility("PCS", "PCS")
    assert compat is True
    assert factor == 1.0
