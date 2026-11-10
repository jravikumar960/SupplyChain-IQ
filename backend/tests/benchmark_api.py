import time
import statistics
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal, Base, engine
from backend.app.services.data_generator import generate_synthetic_data
from backend.app.services.shortage_engine import detect_and_save_shortages
from backend.app.services.mitigation_engine import generate_mitigations_for_shortages

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

def benchmark_apis():
    # Ensure database tables exist and are populated with synthetic dataset
    Base.metadata.create_all(bind=engine)
    generate_synthetic_data()
    db = SessionLocal()
    detect_and_save_shortages(db)
    generate_mitigations_for_shortages(db)
    db.close()

    client = TestClient(app)

    # Warm-up requests
    for _ in range(5):
        client.get("/api/dashboard/summary")
        client.get("/api/dashboard/charts")
        client.post("/api/simulation/run?run_name=Warmup&demand_multiplier=1.0&supplier_capacity_multiplier=1.0&lead_time_delay_days=0")

    num_requests = 50

    # Benchmark Dashboard Summary API
    summary_times = []
    for _ in range(num_requests):
        t0 = time.perf_counter()
        resp = client.get("/api/dashboard/summary")
        t1 = time.perf_counter()
        assert resp.status_code == 200
        summary_times.append((t1 - t0) * 1000.0)

    # Benchmark Dashboard Charts API
    charts_times = []
    for _ in range(num_requests):
        t0 = time.perf_counter()
        resp = client.get("/api/dashboard/charts")
        t1 = time.perf_counter()
        assert resp.status_code == 200
        charts_times.append((t1 - t0) * 1000.0)

    # Benchmark Scenario Simulation API
    sim_times = []
    for i in range(20):
        t0 = time.perf_counter()
        resp = client.post(f"/api/simulation/run?run_name=API+Bench+{i}&demand_multiplier=1.2&supplier_capacity_multiplier=0.8&lead_time_delay_days=7")
        t1 = time.perf_counter()
        assert resp.status_code == 200
        sim_times.append((t1 - t0) * 1000.0)

    print("=" * 60)
    print("SUPPLYCHAIN IQ — API ENDPOINT PERFORMANCE BENCHMARK")
    print("=" * 60)
    print(f"Test Environment: FastAPI TestClient (includes DB access + JSON serialization)")
    print(f"Request Count: {num_requests} per GET endpoint, 20 for POST simulation")
    print("-" * 60)
    print(f"Dashboard Summary API (/api/dashboard/summary):")
    print(f"  Median (p50): {statistics.median(summary_times):.3f} ms | p95: {percentile(summary_times, 95):.3f} ms")
    print(f"Dashboard Charts API (/api/dashboard/charts):")
    print(f"  Median (p50): {statistics.median(charts_times):.3f} ms | p95: {percentile(charts_times, 95):.3f} ms")
    print(f"Simulation Run API (/api/simulation/run):")
    print(f"  Median (p50): {statistics.median(sim_times):.3f} ms | p95: {percentile(sim_times, 95):.3f} ms")
    print("=" * 60)

if __name__ == "__main__":
    benchmark_apis()
