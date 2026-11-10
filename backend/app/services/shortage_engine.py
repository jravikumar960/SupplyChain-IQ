from sqlalchemy.orm import Session
from backend.app.models.models import SKU, Location, ForecastDemand, Shortage, LeadTime, SupplierCapacity, DataIssue
from backend.app.services.inventory_engine import calculate_projected_inventory
from backend.app.services.prioritization_engine import calculate_priority_score
import random

def detect_and_save_shortages(db: Session):
    # Clear existing shortages
    db.query(Shortage).delete()
    db.commit()

    demands = db.query(ForecastDemand).all()
    shortages_created = []

    for d in demands:
        inv_proj = calculate_projected_inventory(db, d.sku_id, d.location_id, d.week_start)
        proj_avail = inv_proj["projected_available"]
        safety = inv_proj["safety_stock"]

        # If projected available falls below safety stock or < 0
        threshold = safety
        if proj_avail < threshold:
            shortage_qty = round(threshold - proj_avail, 2)

            # Determine root cause
            sku = db.query(SKU).filter(SKU.sku_id == d.sku_id).first()
            lt = db.query(LeadTime).filter(LeadTime.sku_id == d.sku_id).first()

            root_cause = "Insufficient opening stock"
            if d.forecast_quantity > 800:
                root_cause = "Demand spike"
            elif not lt:
                root_cause = "Missing supplier information (Lead time missing)"
            elif sku and sku.criticality == "Critical":
                root_cause = "Supplier capacity shortage / High criticality constraint"

            # Severity
            severity = "Medium"
            if shortage_qty > 500 or (sku and sku.criticality == "Critical"):
                severity = "Critical"
            elif shortage_qty > 200:
                severity = "High"
            elif shortage_qty < 50:
                severity = "Low"

            priority_score = calculate_priority_score(severity, sku.criticality if sku else "Medium", shortage_qty)

            shortage_id = f"SHORT-{d.sku_id}-{d.location_id}-{d.week_start}"
            shortage = Shortage(
                shortage_id=shortage_id,
                sku_id=d.sku_id,
                location_id=d.location_id,
                week_start=d.week_start,
                demand_quantity=d.forecast_quantity,
                projected_available=proj_avail,
                shortage_quantity=shortage_qty,
                severity=severity,
                root_cause=root_cause,
                priority_score=priority_score,
                status="Open"
            )
            db.add(shortage)
            shortages_created.append(shortage)

    db.commit()
    return len(shortages_created)
