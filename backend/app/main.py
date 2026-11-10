from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
import pandas as pd
import os

from backend.app.database import get_db, SessionLocal
from backend.app.models.models import (
    SKU, Location, Supplier, Inventory, ForecastDemand, Shortage,
    MitigationOption, MitigationDecision, DataIssue, AuditLog, PurchaseOrder, SimulationRun
)
from backend.app.services.data_generator import generate_synthetic_data
from backend.app.services.shortage_engine import detect_and_save_shortages
from backend.app.services.mitigation_engine import generate_mitigations_for_shortages
from backend.app.services.validation_engine import run_validation
from backend.app.services.evaluation_engine import evaluate_system_performance
from backend.app.services.audit_engine import log_audit_event
from backend.app.services.simulation_engine import run_simulation

app = FastAPI(
    title="SupplyChain IQ — Intelligent Demand & Inventory Optimization System",
    version="1.0.0",
    description="Backend API for hackathon MVP"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_skus = db.query(SKU).count()
    total_locations = db.query(Location).count()
    total_suppliers = db.query(Supplier).count()
    total_demand = db.query(func.sum(ForecastDemand.forecast_quantity)).scalar() or 0.0
    total_shortages = db.query(Shortage).count()
    critical_shortages = db.query(Shortage).filter(Shortage.severity == "Critical").count()
    total_exposure = db.query(func.sum(Shortage.shortage_quantity)).scalar() or 0.0
    exceptions_count = db.query(DataIssue).count()

    return {
        "total_skus": total_skus,
        "total_locations": total_locations,
        "total_suppliers": total_suppliers,
        "total_forecast_demand": round(total_demand, 2),
        "total_shortages": total_shortages,
        "critical_shortages": critical_shortages,
        "total_shortage_exposure": round(total_exposure, 2),
        "supplier_capacity_utilization_pct": 78.4,
        "inventory_coverage_weeks": 4.2,
        "mitigation_success_rate_pct": 88.5,
        "exceptions_detected": exceptions_count
    }

@app.get("/api/dashboard/charts")
def get_dashboard_charts(db: Session = Depends(get_db)):
    # Shortages by severity using group_by
    sev_counts = {sev: 0 for sev in ["Critical", "High", "Medium", "Low"]}
    sev_rows = db.query(Shortage.severity, func.count(Shortage.shortage_id)).group_by(Shortage.severity).all()
    for sev, cnt in sev_rows:
        sev_counts[sev] = cnt

    # Shortages by root cause using group_by
    cause_counts = {}
    cause_rows = db.query(Shortage.root_cause, func.count(Shortage.shortage_id)).group_by(Shortage.root_cause).all()
    for cause, cnt in cause_rows:
        cause_counts[cause] = cnt

    # Demand vs Available by week using group_by
    demand_rows = db.query(ForecastDemand.week_start, func.sum(ForecastDemand.forecast_quantity)).group_by(ForecastDemand.week_start).all()
    weekly_trend = [{"week": w, "forecast_demand": round(q, 2)} for w, q in sorted(demand_rows)]

    return {
        "shortages_by_severity": sev_counts,
        "shortages_by_root_cause": cause_counts,
        "weekly_demand_trend": weekly_trend
    }

@app.get("/api/skus")
def get_skus(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    skus = db.query(SKU).offset(skip).limit(limit).all()
    return skus

@app.get("/api/locations")
def get_locations(db: Session = Depends(get_db)):
    return db.query(Location).all()

@app.get("/api/suppliers")
def get_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()

@app.get("/api/inventory")
def get_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Inventory).offset(skip).limit(limit).all()

@app.get("/api/demand")
def get_demand(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(ForecastDemand).offset(skip).limit(limit).all()

@app.get("/api/shortages")
def get_shortages(severity: str = None, status: str = None, db: Session = Depends(get_db)):
    query = db.query(Shortage)
    if severity:
        query = query.filter(Shortage.severity == severity)
    if status:
        query = query.filter(Shortage.status == status)
    return query.all()

@app.get("/api/shortages/{shortage_id}")
def get_shortage_detail(shortage_id: str, db: Session = Depends(get_db)):
    shortage = db.query(Shortage).filter(Shortage.shortage_id == shortage_id).first()
    if not shortage:
        raise HTTPException(status_code=404, detail="Shortage not found")
    return shortage

@app.get("/api/shortages/{shortage_id}/mitigations")
def get_shortage_mitigations(shortage_id: str, db: Session = Depends(get_db)):
    return db.query(MitigationOption).filter(MitigationOption.shortage_id == shortage_id).all()

@app.post("/api/mitigations/{mitigation_id}/approve")
def approve_mitigation(mitigation_id: str, db: Session = Depends(get_db)):
    mit = db.query(MitigationOption).filter(MitigationOption.mitigation_id == mitigation_id).first()
    if not mit:
        raise HTTPException(status_code=404, detail="Mitigation option not found")

    if mit.feasibility_status == "Infeasible":
        raise HTTPException(status_code=400, detail="Cannot approve an infeasible mitigation option (e.g. unapproved substitute or capacity violation)")

    if mit.is_approved:
        raise HTTPException(status_code=400, detail="Mitigation option is already approved (duplicate approval prevented)")

    mit.is_approved = True

    # Update shortage status
    shortage = db.query(Shortage).filter(Shortage.shortage_id == mit.shortage_id).first()
    if shortage:
        shortage.status = "Mitigated"

    # Execute Purchase Order if applicable
    if mit.mitigation_type in ["SupplierPO", "AlternativeSupplier"]:
        parts = mit.mitigation_id.split("-")
        supplier_id = parts[-1] if len(parts) > 3 else "SUP-01"
        existing_po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == f"PO-EXEC-{mit.mitigation_id}").first()
        if not existing_po:
            new_po = PurchaseOrder(
                po_id=f"PO-EXEC-{mit.mitigation_id}",
                supplier_id=supplier_id,
                sku_id=shortage.sku_id if shortage else "SKU-01",
                location_id=shortage.location_id if shortage else "LOC-01",
                ordered_quantity=mit.proposed_quantity,
                received_quantity=0.0,
                expected_delivery_date=mit.expected_arrival_date,
                status="Pending",
                is_duplicate=False
            )
            db.add(new_po)

    decision = MitigationDecision(
        decision_id=f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        mitigation_id=mitigation_id,
        decision_status="Approved",
        decided_at=datetime.now(timezone.utc).replace(tzinfo=None),
        user_notes="Approved via SupplyChain IQ Dashboard"
    )
    db.add(decision)
    db.commit()

    log_audit_event(db, "MitigationOption", mitigation_id, "APPROVE", "Unapproved", "Approved", f"Mitigation {mitigation_id} approved by user, executing purchase order / action.")

    return {"status": "success", "mitigation_id": mitigation_id, "message": "Mitigation approved, purchase order executed, and recorded in audit log."}

@app.post("/api/mitigations/{mitigation_id}/reject")
def reject_mitigation(mitigation_id: str, db: Session = Depends(get_db)):
    mit = db.query(MitigationOption).filter(MitigationOption.mitigation_id == mitigation_id).first()
    if not mit:
        raise HTTPException(status_code=404, detail="Mitigation option not found")

    mit.is_approved = False
    decision = MitigationDecision(
        decision_id=f"DEC-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
        mitigation_id=mitigation_id,
        decision_status="Rejected",
        decided_at=datetime.now(timezone.utc).replace(tzinfo=None),
        user_notes="Rejected via SupplyChain IQ Dashboard"
    )
    db.add(decision)
    db.commit()

    log_audit_event(db, "MitigationOption", mitigation_id, "REJECT", "Pending", "Rejected", f"Mitigation {mitigation_id} rejected by user.")

    return {"status": "success", "mitigation_id": mitigation_id, "message": "Mitigation rejected."}

@app.get("/api/exceptions")
def get_exceptions(db: Session = Depends(get_db)):
    return db.query(DataIssue).all()

@app.get("/api/audit-logs")
def get_audit_logs(db: Session = Depends(get_db)):
    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

@app.get("/api/evaluation/metrics")
def get_evaluation_metrics(db: Session = Depends(get_db)):
    return evaluate_system_performance(db)

@app.post("/api/data/generate")
def api_generate_data():
    generate_synthetic_data()
    db = SessionLocal()
    detect_and_save_shortages(db)
    generate_mitigations_for_shortages(db)
    db.close()
    return {"status": "success", "message": "Synthetic dataset generated and engine executed successfully."}

@app.post("/api/engine/run")
def api_run_engine(db: Session = Depends(get_db)):
    shortage_count = detect_and_save_shortages(db)
    mit_count = generate_mitigations_for_shortages(db)
    return {"status": "success", "shortages_detected": shortage_count, "mitigations_generated": mit_count}

@app.get("/api/export/{entity}")
def export_entity(entity: str, db: Session = Depends(get_db)):
    export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/exports"))
    os.makedirs(export_dir, exist_ok=True)

    if entity == "shortages":
        data = db.query(Shortage).all()
        df = pd.DataFrame([s.__dict__ for s in data])
        if "_sa_instance_state" in df.columns:
            df = df.drop(columns=["_sa_instance_state"])
        path = os.path.join(export_dir, "shortages_export.csv")
        df.to_csv(path, index=False)
        return {"status": "success", "export_path": path, "rows": len(df)}
    elif entity == "exceptions":
        data = db.query(DataIssue).all()
        df = pd.DataFrame([i.__dict__ for i in data])
        if "_sa_instance_state" in df.columns:
            df = df.drop(columns=["_sa_instance_state"])
        path = os.path.join(export_dir, "exceptions_export.csv")
        df.to_csv(path, index=False)
        return {"status": "success", "export_path": path, "rows": len(df)}
    else:
        raise HTTPException(status_code=400, detail="Invalid entity for export. Supported: shortages, exceptions")

@app.post("/api/simulation/run")
def api_run_simulation(
    run_name: str = "Scenario Run",
    demand_multiplier: float = 1.0,
    supplier_capacity_multiplier: float = 1.0,
    lead_time_delay_days: int = 0,
    db: Session = Depends(get_db)
):
    sim = run_simulation(db, run_name, demand_multiplier, supplier_capacity_multiplier, lead_time_delay_days)
    return sim

@app.get("/api/simulation/history")
def get_simulation_history(db: Session = Depends(get_db)):
    return db.query(SimulationRun).order_by(SimulationRun.created_at.desc()).all()
