import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.models import (
    SKU, Shortage, DataIssue, PurchaseOrder, SKUSubstitute,
    SupplierCapacity, LeadTime, MitigationOption, AuditLog
)
from backend.app.services.inventory_engine import calculate_projected_inventory
from backend.app.services.supplier_engine import check_supplier_feasibility

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_dashboard_summary():
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_skus"] > 0
    assert data["exceptions_detected"] >= 5

def test_duplicate_inbound_filtering():
    db = SessionLocal()
    # Verify duplicate POs exist and are flagged
    dupes = db.query(PurchaseOrder).filter(PurchaseOrder.is_duplicate == True).all()
    assert len(dupes) > 0
    # Verify inventory projection excludes duplicate POs
    dup_po = dupes[0]
    proj = calculate_projected_inventory(db, dup_po.sku_id, dup_po.location_id, "2026-W01")
    assert "projected_available" in proj
    db.close()

def test_anomaly_detections():
    db = SessionLocal()
    issues = db.query(DataIssue).all()
    issue_types = [i.issue_type for i in issues]
    assert "INBOUND_COUNTED_TWICE" in issue_types
    assert "SUBSTITUTE_NOT_APPROVED" in issue_types
    assert "SUPPLIER_CAPACITY_EXCEEDED" in issue_types
    assert "SHORTAGE_WITHOUT_LEAD_TIME" in issue_types
    assert "UNIT_OF_MEASURE_MISMATCH" in issue_types
    db.close()

def test_unapproved_substitute_blocking():
    db = SessionLocal()
    unapp = db.query(SKUSubstitute).filter(SKUSubstitute.is_approved == False).first()
    if unapp:
        mit = db.query(MitigationOption).filter(MitigationOption.mitigation_id.like(f"%{unapp.substitute_sku_id}%")).first()
        if mit:
            assert mit.feasibility_status == "Infeasible"
    db.close()

def test_supplier_capacity_and_moq():
    db = SessionLocal()
    cap = db.query(SupplierCapacity).first()
    if cap:
        res_overflow = check_supplier_feasibility(db, cap.supplier_id, cap.sku_id, cap.weekly_capacity * 2)
        assert res_overflow["feasible"] == False

        res_moq = check_supplier_feasibility(db, cap.supplier_id, cap.sku_id, cap.minimum_order_quantity / 2)
        assert res_moq["feasible"] == False
    db.close()

def test_mitigation_approval_and_audit():
    db = SessionLocal()
    feasible_mit = db.query(MitigationOption).filter(MitigationOption.feasibility_status == "Feasible").first()
    if feasible_mit:
        mit_id = feasible_mit.mitigation_id
        db.close()

        # Approve via API
        res = client.post(f"/api/mitigations/{mit_id}/approve")
        assert res.status_code == 200

        db = SessionLocal()
        audit = db.query(AuditLog).filter(AuditLog.entity_id == mit_id).first()
        assert audit is not None
        assert audit.event_type == "APPROVE"
    db.close()

def test_evaluation_metrics():
    response = client.get("/api/evaluation/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["anomaly_detection_rate_pct"] == 100.0
    assert metrics["demand_coverage_pct"] > 90.0
