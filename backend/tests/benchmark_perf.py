import time
import statistics
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Inventory, ForecastDemand, PurchaseOrder, ProductionPlan, Shortage, SimulationRun, SupplierCapacity
)
from backend.app.services.inventory_engine import calculate_projected_inventory
from backend.app.services.shortage_engine import detect_and_save_shortages
from backend.app.services.prioritization_engine import calculate_priority_score
from backend.app.services.simulation_engine import run_simulation

def percentile(data, p):
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[f]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

def run_benchmarks():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Seed identical deterministic test data
    sku1 = SKU(sku_id="SKU-SIM-1", sku_name="Simulation SKU 1", category="Electronics", unit_of_measure="PCS", unit_cost=100.0, criticality="Critical", is_active=True)
    loc1 = Location(location_id="LOC-SIM-1", location_name="Warehouse North", location_type="Warehouse", region="North", storage_capacity=10000.0)
    inv1 = Inventory(inventory_id="INV-SIM-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", on_hand_quantity=500.0, reserved_quantity=50.0, safety_stock=100.0)
    dem1 = ForecastDemand(demand_id="DEM-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", week_start="2026-W01", forecast_quantity=200.0)
    dem2 = ForecastDemand(demand_id="DEM-2", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", week_start="2026-W02", forecast_quantity=300.0)
    po1 = PurchaseOrder(po_id="PO-SIM-1", supplier_id="SUP-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", ordered_quantity=100.0, received_quantity=0.0, expected_delivery_date="2026-01-05", status="Pending", is_duplicate=False)
    prod1 = ProductionPlan(production_id="PROD-SIM-1", sku_id="SKU-SIM-1", location_id="LOC-SIM-1", planned_quantity=100.0, production_start="2026-01-03", production_end="2026-01-05", capacity_available=500.0, status="Planned")
    cap1 = SupplierCapacity(capacity_id="CAP-1", supplier_id="SUP-1", sku_id="SKU-SIM-1", weekly_capacity=200.0, minimum_order_quantity=50.0, effective_from="2026-01-01", effective_to="2026-12-31")

    db.add_all([sku1, loc1, inv1, dem1, dem2, po1, prod1, cap1])
    db.commit()

    # Warm-up phase
    for _ in range(5):
        calculate_projected_inventory(db, "SKU-SIM-1", "LOC-SIM-1", "2026-W02")
        detect_and_save_shortages(db)
        calculate_priority_score("Critical", "Critical", 250.0)
        run_simulation(db, "Warmup Run", demand_multiplier=1.2, supplier_capacity_multiplier=0.8, lead_time_delay_days=7)

    # Benchmark 1: Inventory Projection (100 measured iterations)
    inv_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        calculate_projected_inventory(db, "SKU-SIM-1", "LOC-SIM-1", "2026-W02")
        t1 = time.perf_counter()
        inv_times.append((t1 - t0) * 1000.0) # ms

    # Benchmark 2: Shortage Detection (50 measured iterations)
    shortage_times = []
    for _ in range(50):
        t0 = time.perf_counter()
        detect_and_save_shortages(db)
        t1 = time.perf_counter()
        shortage_times.append((t1 - t0) * 1000.0)

    # Benchmark 3: Prioritization Calculation (1000 measured iterations, reported in microseconds)
    prio_times = []
    for _ in range(1000):
        t0 = time.perf_counter()
        calculate_priority_score("Critical", "Critical", 250.0)
        t1 = time.perf_counter()
        prio_times.append((t1 - t0) * 1_000_000.0) # microseconds

    # Benchmark 4: Scenario Simulation (30 measured iterations)
    sim_times = []
    for i in range(30):
        t0 = time.perf_counter()
        run_simulation(db, f"Bench Run {i}", demand_multiplier=1.2, supplier_capacity_multiplier=0.8, lead_time_delay_days=7)
        t1 = time.perf_counter()
        sim_times.append((t1 - t0) * 1000.0)

    print("=" * 60)
    print("SUPPLYCHAIN IQ — RIGOROUS PERFORMANCE BENCHMARK REPORT")
    print("=" * 60)
    print(f"Dataset: 1 SKU, 1 Location, 2 Forecast Weeks, 1 PO, 1 Production Plan, 1 Supplier Capacity")
    print("-" * 60)
    print(f"Inventory Projection (ms):")
    print(f"  Median (p50): {statistics.median(inv_times):.3f} ms | p95: {percentile(inv_times, 95):.3f} ms")
    print(f"Shortage Detection (ms):")
    print(f"  Median (p50): {statistics.median(shortage_times):.3f} ms | p95: {percentile(shortage_times, 95):.3f} ms")
    print(f"Prioritization Calculation (microseconds):")
    print(f"  Median (p50): {statistics.median(prio_times):.3f} µs | p95: {percentile(prio_times, 95):.3f} µs")
    print(f"Scenario Simulation (ms):")
    print(f"  Median (p50): {statistics.median(sim_times):.3f} ms | p95: {percentile(sim_times, 95):.3f} ms")
    print("=" * 60)

    db.close()

if __name__ == "__main__":
    run_benchmarks()
