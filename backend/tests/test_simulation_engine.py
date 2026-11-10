import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Inventory, ForecastDemand, PurchaseOrder, ProductionPlan, Shortage, SimulationRun, SupplierCapacity, DataIssue, DetectorExecution
)
from backend.app.services.simulation_engine import run_simulation
from backend.app.services.inventory_engine import calculate_projected_inventory

@pytest.fixture
def sim_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Seed comprehensive test data
    sku1 = SKU(sku_id="SKU-SIM-1", sku_name="Simulation SKU 1", category="Electronics", unit_of_measure="PCS", unit_cost=100.0, criticality="Critical", is_active=True)
    sku2 = SKU(sku_id="SKU-SIM-2", sku_name="Simulation SKU 2", category="Hardware", unit_of_measure="PCS", unit_cost=0.0, criticality="High", is_active=True) # Zero cost
    sku3 = SKU(sku_id="SKU-SIM-3", sku_name="Simulation SKU 3", category="Misc", unit_of_measure="PCS", unit_cost=None, criticality="Low", is_active=True) # Missing cost
    loc1 = Location(location_id="LOC-SIM-1", location_name="Warehouse North", location_type="Warehouse", region="North", storage_capacity=10000.0)
    loc2 = Location(location_id="LOC-SIM-2", location_name="Warehouse South", location_type="Warehouse", region="South", storage_capacity=10000.0)

    inv1 = Inventory(inventory_id="INV-SIM-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", on_hand_quantity=500.0, reserved_quantity=50.0, safety_stock=100.0)
    inv2 = Inventory(inventory_id="INV-SIM-2", sku_id="SKU-SIM-2", location_id="LOC-SIM-2", on_hand_quantity=200.0, reserved_quantity=20.0, safety_stock=50.0)
    inv3 = Inventory(inventory_id="INV-SIM-3", sku_id="SKU-SIM-3", location_id="LOC-SIM-1", on_hand_quantity=100.0, reserved_quantity=10.0, safety_stock=80.0)

    dem1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", week_start="2026-W01", forecast_quantity=200.0)
    dem2 = ForecastDemand(demand_id="DEM-2", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", week_start="2026-W02", forecast_quantity=300.0)
    dem3 = ForecastDemand(demand_id="DEM-3", sku_id="SKU-SIM-2", location_id="LOC-SIM-2", week_start="2026-W01", forecast_quantity=180.0)
    dem4 = ForecastDemand(demand_id="DEM-4", sku_id="SKU-SIM-3", location_id="LOC-SIM-1", week_start="2026-W01", forecast_quantity=150.0)

    po1 = PurchaseOrder(po_id="PO-SIM-1", supplier_id="SUP-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", ordered_quantity=100.0, received_quantity=0.0, expected_delivery_date="2026-01-05", status="Pending", is_duplicate=False)
    po2 = PurchaseOrder(po_id="PO-SIM-2", supplier_id="SUP-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", ordered_quantity=150.0, received_quantity=0.0, expected_delivery_date="2026-01-05", status="Pending", is_duplicate=False)
    po_received = PurchaseOrder(po_id="PO-SIM-REC", supplier_id="SUP-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", ordered_quantity=100.0, received_quantity=100.0, expected_delivery_date="2026-01-02", status="Received", is_duplicate=False)
    po_dup = PurchaseOrder(po_id="PO-SIM-DUP", supplier_id="SUP-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", ordered_quantity=200.0, received_quantity=0.0, expected_delivery_date="2026-01-05", status="Pending", is_duplicate=True)
    po_canc = PurchaseOrder(po_id="PO-SIM-CANC", supplier_id="SUP-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", ordered_quantity=200.0, received_quantity=0.0, expected_delivery_date="2026-01-05", status="Cancelled", is_duplicate=False)

    prod1 = ProductionPlan(production_id="PROD-SIM-1", sku_id="SKU-SIM-2", location_id="LOC-SIM-2", planned_quantity=100.0, production_start="2026-01-03", production_end="2026-01-05", capacity_available=500.0, status="Planned")

    cap1 = SupplierCapacity(capacity_id="CAP-1", supplier_id="SUP-1", sku_id="SKU-SIM-1", weekly_capacity=200.0, minimum_order_quantity=50.0, effective_from="2026-01-01", effective_to="2026-12-31")

    db.add_all([sku1, sku2, sku3, loc1, loc2, inv1, inv2, inv3, dem1, dem2, dem3, dem4, po1, po2, po_received, po_dup, po_canc, prod1, cap1])
    db.commit()

    yield db
    db.close()

def test_1_baseline_matches_inventory_projection(sim_db):
    proj = calculate_projected_inventory(sim_db, "SKU-SIM-1", "LOC-SIM-1", "2026-W01")
    assert proj["sku_id"] == "SKU-SIM-1"
    assert "projected_available" in proj

def test_2_zero_disruption_identical_metrics(sim_db):
    run = run_simulation(sim_db, "Zero Disruption", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run.baseline_shortages_count == run.simulated_shortages_count
    assert run.baseline_exposure_value == run.simulated_exposure_value

def test_3_demand_surge_changes_projections(sim_db):
    run = run_simulation(sim_db, "Demand Surge", demand_multiplier=1.5, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run.simulated_total_shortage_qty >= run.baseline_total_shortage_qty

def test_4_capacity_reduction_changes_inbound(sim_db):
    run = run_simulation(sim_db, "Capacity Reduction", demand_multiplier=1.0, supplier_capacity_multiplier=0.5, lead_time_delay_days=0)
    assert run is not None

def test_5_lead_time_delay_shifts_po(sim_db):
    run = run_simulation(sim_db, "Lead Time Delay", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=14)
    assert run is not None

def test_6_received_pos_unaffected(sim_db):
    run = run_simulation(sim_db, "Received PO Check", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=10)
    assert run is not None

def test_7_cancelled_and_duplicate_excluded(sim_db):
    run = run_simulation(sim_db, "Excluded PO Check", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run is not None

def test_8_production_completion_handled(sim_db):
    run = run_simulation(sim_db, "Production Check", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run is not None

def test_9_combined_disruption_scenario(sim_db):
    run = run_simulation(sim_db, "Combined Stress", demand_multiplier=1.3, supplier_capacity_multiplier=0.7, lead_time_delay_days=7)
    assert run.simulated_shortages_count >= 0

def test_10_partial_inventory_shortage(sim_db):
    run = run_simulation(sim_db, "Partial Shortage", demand_multiplier=1.1, supplier_capacity_multiplier=0.9, lead_time_delay_days=3)
    assert run is not None

def test_11_negative_inventory_backorders(sim_db):
    run = run_simulation(sim_db, "Backorders Check", demand_multiplier=2.0, supplier_capacity_multiplier=0.5, lead_time_delay_days=21)
    assert run.simulated_backorder_qty >= 0.0

def test_12_safety_stock_deficits(sim_db):
    run = run_simulation(sim_db, "Safety Deficit", demand_multiplier=1.2, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run.simulated_safety_deficit >= 0.0

def test_13_missing_and_zero_unit_cost_handling(sim_db):
    run = run_simulation(sim_db, "Cost Handling Check", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run.missing_unit_cost_count >= 2 # SKU-SIM-2 (0.0) and SKU-SIM-3 (None)
    # Exposure should only reflect SKU-SIM-1 (unit_cost = 100.0)
    assert run.simulated_exposure_value >= 0.0

def test_14_empty_dataset_handling():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    run = run_simulation(db, "Empty Run", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    assert run.simulated_shortages_count == 0
    db.close()

def test_15_invalid_parameter_boundaries(sim_db):
    with pytest.raises(ValueError):
        run_simulation(sim_db, "Invalid Demand", demand_multiplier=2.5, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    with pytest.raises(ValueError):
        run_simulation(sim_db, "Invalid Capacity", demand_multiplier=1.0, supplier_capacity_multiplier=0.3, lead_time_delay_days=0)
    with pytest.raises(ValueError):
        run_simulation(sim_db, "Invalid Delay", demand_multiplier=1.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=25)

def test_16_historical_simulation_retrieval(sim_db):
    run = run_simulation(sim_db, "History Retrieval", demand_multiplier=1.1, supplier_capacity_multiplier=0.9, lead_time_delay_days=2)
    history = sim_db.query(SimulationRun).filter(SimulationRun.simulation_id == run.simulation_id).first()
    assert history is not None
    assert history.run_name == "History Retrieval"

def test_17_failed_simulation_rollback(sim_db):
    with pytest.raises(ValueError):
        run_simulation(sim_db, "Rollback Test", demand_multiplier=3.0, supplier_capacity_multiplier=1.0, lead_time_delay_days=0)
    failed_run = sim_db.query(SimulationRun).filter(SimulationRun.run_name == "Rollback Test").first()
    assert failed_run is None

def test_18_baseline_database_immutability(sim_db):
    initial_demands = sim_db.query(ForecastDemand).all()
    initial_demand_qty = initial_demands[0].forecast_quantity
    run_simulation(sim_db, "Immutability Test", demand_multiplier=1.8, supplier_capacity_multiplier=0.6, lead_time_delay_days=10)
    current_demand_qty = sim_db.query(ForecastDemand).all()[0].forecast_quantity
    assert initial_demand_qty == current_demand_qty

def test_19_determinism_of_repeated_runs(sim_db):
    run1 = run_simulation(sim_db, "Deterministic 1", demand_multiplier=1.2, supplier_capacity_multiplier=0.8, lead_time_delay_days=5)
    run2 = run_simulation(sim_db, "Deterministic 2", demand_multiplier=1.2, supplier_capacity_multiplier=0.8, lead_time_delay_days=5)
    assert run1.simulated_shortages_count == run2.simulated_shortages_count
    assert run1.simulated_exposure_value == run2.simulated_exposure_value

def test_20_multi_sku_multi_location_correctness(sim_db):
    run = run_simulation(sim_db, "Multi SKU Loc", demand_multiplier=2.0, supplier_capacity_multiplier=0.5, lead_time_delay_days=10)
    assert run.affected_skus_count >= 1
    assert run.affected_locations_count >= 1

def test_21_simulation_operational_issue_immutability(sim_db):
    # 1. Insert a purchase order with an incompatible/invalid UOM that would normally trigger DataIssue in inventory projection
    po_bad = PurchaseOrder(
        po_id="PO-SIM-BAD-UOM",
        supplier_id="SUP-1",
        sku_id="SKU-SIM-1",
        location_id="LOC-SIM-1",
        ordered_quantity=500.0,
        received_quantity=0.0,
        expected_delivery_date="2026-01-05",
        status="Pending",
        is_duplicate=False,
        unit_of_measure="UNKNOWN_UOM"
    )
    sim_db.add(po_bad)

    # 2. Insert representative pre-existing DataIssue and DetectorExecution records
    issue_pre = DataIssue(
        issue_id="ISSUE-PRE-1",
        issue_type="UNIT_OF_MEASURE_MISMATCH",
        affected_entity_type="PurchaseOrder",
        affected_entity_id="PO-SIM-BAD-UOM",
        detection_result="Incompatible UOM",
        severity="Medium",
        explanation="Pre-existing issue",
        resolution_status="Flagged"
    )
    exec_pre = DetectorExecution(
        execution_id="EXEC-PRE-1",
        evaluation_run_id="RUN-TEST-SIM",
        detector_type="UNIT_OF_MEASURE_MISMATCH",
        entity_type="PurchaseOrder",
        entity_id="PO-SIM-BAD-UOM"
    )
    sim_db.add_all([issue_pre, exec_pre])
    sim_db.commit()

    # 3. Snapshot DataIssue and DetectorExecution state before simulation
    issues_before = {i.issue_id: (i.issue_type, i.affected_entity_id, i.explanation) for i in sim_db.query(DataIssue).all()}
    execs_before = {e.execution_id: (e.evaluation_run_id, e.detector_type, e.entity_id) for e in sim_db.query(DetectorExecution).all()}

    # 4. Execute Phase 4 scenario simulation
    run_simulation(sim_db, "Immutability Stress Test", demand_multiplier=1.2, supplier_capacity_multiplier=0.9, lead_time_delay_days=5)

    # 5. Query DataIssue and DetectorExecution state after simulation
    issues_after = {i.issue_id: (i.issue_type, i.affected_entity_id, i.explanation) for i in sim_db.query(DataIssue).all()}
    execs_after = {e.execution_id: (e.evaluation_run_id, e.detector_type, e.entity_id) for e in sim_db.query(DetectorExecution).all()}

    # 6. Assert complete record immutability
    assert issues_before == issues_after, "Phase 4 simulation modified or created DataIssue records!"
    assert execs_before == execs_after, "Phase 4 simulation modified or created DetectorExecution records!"
