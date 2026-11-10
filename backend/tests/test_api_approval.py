import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.models.models import MitigationOption, PurchaseOrder, Shortage

client = TestClient(app)

def test_api_infeasible_approval_returns_400():
    db = SessionLocal()
    infeasible = db.query(MitigationOption).filter(MitigationOption.feasibility_status == "Infeasible").first()
    if infeasible:
        mit_id = infeasible.mitigation_id
        db.close()
        response = client.post(f"/api/mitigations/{mit_id}/approve")
        assert response.status_code == 400
        assert "infeasible" in response.json()["detail"].lower()
    else:
        db.close()

def test_api_feasible_approval_and_duplicate_prevention():
    db = SessionLocal()
    feasible = db.query(MitigationOption).filter(
        MitigationOption.feasibility_status == "Feasible",
        MitigationOption.mitigation_type == "SupplierPO"
    ).first()
    if feasible:
        mit_id = feasible.mitigation_id
        proposed_qty = feasible.proposed_quantity
        feasible.is_approved = False
        db.commit()
        db.close()

        # 1. First approval should succeed (HTTP 200)
        res1 = client.post(f"/api/mitigations/{mit_id}/approve")
        assert res1.status_code == 200
        assert res1.json()["status"] == "success"

        # Verify exactly one purchase order created
        db = SessionLocal()
        pos = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == f"PO-EXEC-{mit_id}").all()
        assert len(pos) == 1
        po = pos[0]
        assert po.ordered_quantity == proposed_qty

        # 2. Duplicate approval should be rejected with HTTP 400
        res2 = client.post(f"/api/mitigations/{mit_id}/approve")
        assert res2.status_code == 400
        assert "already approved" in res2.json()["detail"].lower()

        # Verify no second purchase order was created
        pos_after = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == f"PO-EXEC-{mit_id}").all()
        assert len(pos_after) == 1
        db.close()
    else:
        db.close()

def test_api_reject_mitigation():
    db = SessionLocal()
    feasible = db.query(MitigationOption).filter(MitigationOption.feasibility_status == "Feasible").first()
    if feasible:
        mit_id = feasible.mitigation_id
        db.close()

        res = client.post(f"/api/mitigations/{mit_id}/reject")
        assert res.status_code == 200
        assert res.json()["status"] == "success"
    else:
        db.close()
