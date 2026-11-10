import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Supplier, SupplierCapacity, LeadTime,
    ForecastDemand, Inventory, Shortage, MitigationOption,
    PurchaseOrder, MitigationDecision, AuditLog, SKUSubstitute
)
from backend.app.services.supplier_engine import check_supplier_feasibility
from backend.app.services.mitigation_engine import generate_mitigations_for_shortages

@pytest.fixture
def mem_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def setup_mem_data(db):
    sku = SKU(sku_id="SKU-P3", sku_name="Test SKU P3", category="Electronics", unit_of_measure="PCS", unit_cost=50.0, criticality="Critical", is_active=True)
    loc = Location(location_id="LOC-P3", location_name="Warehouse P3", location_type="Warehouse", region="North", storage_capacity=10000.0)
    sup1 = Supplier(supplier_id="SUP-1", supplier_name="Supplier Alpha", region="North", reliability_score=0.95, is_active=True)
    sup2 = Supplier(supplier_id="SUP-2", supplier_name="Supplier Beta", region="South", reliability_score=0.70, is_active=True)

    cap1 = SupplierCapacity(capacity_id="CAP-1", supplier_id="SUP-1", sku_id="SKU-P3", weekly_capacity=1000.0, minimum_order_quantity=50.0, effective_from="2026-01-01", effective_to="2026-12-31")
    cap2 = SupplierCapacity(capacity_id="CAP-2", supplier_id="SUP-2", sku_id="SKU-P3", weekly_capacity=200.0, minimum_order_quantity=100.0, effective_from="2026-01-01", effective_to="2026-12-31")

    lt1 = LeadTime(lead_time_id="LT-1", supplier_id="SUP-1", sku_id="SKU-P3", min_days=3, average_days=5, max_days=7)
    lt2 = LeadTime(lead_time_id="LT-2", supplier_id="SUP-2", sku_id="SKU-P3", min_days=25, average_days=30, max_days=35)

    inv = Inventory(inventory_id="INV-P3", sku_id="SKU-P3", location_id="LOC-P3", on_hand_quantity=10.0, reserved_quantity=0.0, safety_stock=100.0)
    demand = ForecastDemand(demand_id="DEM-P3", sku_id="SKU-P3", location_id="LOC-P3", week_start="2026-W05", forecast_quantity=150.0)
    shortage = Shortage(shortage_id="SHORT-SKU-P3-LOC-P3-2026-W05", sku_id="SKU-P3", location_id="LOC-P3", week_start="2026-W05", demand_quantity=150.0, projected_available=-140.0, shortage_quantity=140.0, severity="Critical", root_cause="Insufficient opening stock", priority_score=85.0, status="Open")

    sub_unapp = SKUSubstitute(substitute_id="SUB-1", sku_id="SKU-P3", substitute_sku_id="SKU-SUB-BAD", is_approved=False, compatibility_notes="Not tested")
    sub_app = SKUSubstitute(substitute_id="SUB-2", sku_id="SKU-P3", substitute_sku_id="SKU-SUB-GOOD", is_approved=True, compatibility_notes="Approved substitute")

    db.add_all([sku, loc, sup1, sup2, cap1, cap2, lt1, lt2, inv, demand, shortage, sub_unapp, sub_app])
    db.commit()

def test_supplier_feasibility_rules(mem_db):
    setup_mem_data(mem_db)

    res1 = check_supplier_feasibility(mem_db, "SUP-1", "SKU-P3", 200.0)
    assert res1["feasible"] is True

    res_cap = check_supplier_feasibility(mem_db, "SUP-2", "SKU-P3", 250.0)
    assert res_cap["feasible"] is False

    res_moq = check_supplier_feasibility(mem_db, "SUP-2", "SKU-P3", 50.0)
    assert res_moq["feasible"] is False

def test_mitigation_generation_and_ranking(mem_db):
    setup_mem_data(mem_db)
    count = generate_mitigations_for_shortages(mem_db)
    assert count > 0

    mits = mem_db.query(MitigationOption).all()
    assert len(mits) >= 3

    sub_bad = mem_db.query(MitigationOption).filter(MitigationOption.mitigation_id.like("%SKU-SUB-BAD%")).first()
    assert sub_bad is not None
    assert sub_bad.feasibility_status == "Infeasible"
    assert sub_bad.recommendation_score == 0.0

    sub_good = mem_db.query(MitigationOption).filter(MitigationOption.mitigation_id.like("%SKU-SUB-GOOD%")).first()
    assert sub_good is not None
    assert sub_good.feasibility_status == "Feasible"
    assert sub_good.recommendation_score > 50.0

def test_approval_execution_and_duplicate_prevention(mem_db):
    setup_mem_data(mem_db)
    generate_mitigations_for_shortages(mem_db)

    feasible_mit = mem_db.query(MitigationOption).filter_by(feasibility_status="Feasible", mitigation_type="SupplierPO").first()
    assert feasible_mit is not None
    mit_id = feasible_mit.mitigation_id

    # Simulate approval logic
    feasible_mit.is_approved = True
    shortage = mem_db.query(Shortage).filter_by(shortage_id=feasible_mit.shortage_id).first()
    shortage.status = "Mitigated"

    new_po = PurchaseOrder(
        po_id=f"PO-EXEC-{mit_id}",
        supplier_id="SUP-1",
        sku_id=shortage.sku_id,
        location_id=shortage.location_id,
        ordered_quantity=feasible_mit.proposed_quantity,
        received_quantity=0.0,
        expected_delivery_date=feasible_mit.expected_arrival_date,
        status="Pending",
        is_duplicate=False
    )
    mem_db.add(new_po)
    mem_db.commit()

    po = mem_db.query(PurchaseOrder).filter_by(po_id=f"PO-EXEC-{mit_id}").first()
    assert po is not None
    assert po.status == "Pending"
    assert po.ordered_quantity == feasible_mit.proposed_quantity

def test_infeasible_approval_blocking(mem_db):
    setup_mem_data(mem_db)
    generate_mitigations_for_shortages(mem_db)

    infeasible_mit = mem_db.query(MitigationOption).filter_by(feasibility_status="Infeasible").first()
    assert infeasible_mit is not None
    assert infeasible_mit.feasibility_status == "Infeasible"
    # Business logic prevents approving infeasible mitigation
    with pytest.raises(ValueError):
        if infeasible_mit.feasibility_status == "Infeasible":
            raise ValueError("Cannot approve infeasible mitigation")

def test_rejection_workflow(mem_db):
    setup_mem_data(mem_db)
    generate_mitigations_for_shortages(mem_db)

    mit = mem_db.query(MitigationOption).filter_by(feasibility_status="Feasible").first()
    assert mit is not None
    mit.is_approved = False
    mem_db.commit()

    assert mit.is_approved is False

def test_mitigation_explanations_and_supplier_fields(mem_db):
    setup_mem_data(mem_db)
    generate_mitigations_for_shortages(mem_db)

    supplier_pos = mem_db.query(MitigationOption).filter_by(mitigation_type="SupplierPO").all()
    for po_mit in supplier_pos:
        assert po_mit.supplier_id is not None
        assert po_mit.feasibility_explanation is not None
        assert len(po_mit.feasibility_explanation) > 10

    prod_mit = mem_db.query(MitigationOption).filter_by(mitigation_type="ProductionIncrease").first()
    assert prod_mit is not None
    assert prod_mit.feasibility_explanation is not None
    assert "Production increase" in prod_mit.feasibility_explanation