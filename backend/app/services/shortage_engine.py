from sqlalchemy.orm import Session
from backend.app.models.models import SKU, Location, ForecastDemand, Shortage, LeadTime
from backend.app.services.inventory_engine import calculate_projected_inventory
from backend.app.services.prioritization_engine import calculate_priority_score

def detect_and_save_shortages(db: Session):
    """
    Detects shortages based on sequential inventory projections and saves them transactionally.
    Guarantees atomicity via nested savepoints.
    """
    try:
        demands = db.query(ForecastDemand).all()
        shortages_data = []

        for d in demands:
            inv_proj = calculate_projected_inventory(db, d.sku_id, d.location_id, d.week_start)
            proj_avail = inv_proj["projected_available"]
            safety = inv_proj["safety_stock"]
            demand_qty = inv_proj["demand_quantity"]

            # Unmet demand (backorder) and safety-stock deficit calculated independently
            unmet_demand = max(0.0, -proj_avail) if proj_avail < 0 else 0.0
            safety_stock_deficit = max(0.0, safety - proj_avail) if proj_avail < safety else 0.0

            # Shortage condition: projected available inventory falls below safety stock threshold
            if proj_avail < safety:
                shortage_qty = round(safety_stock_deficit, 2)

                # Determine root cause
                sku = db.query(SKU).filter(SKU.sku_id == d.sku_id).first()
                lt = db.query(LeadTime).filter(LeadTime.sku_id == d.sku_id).first()

                root_cause = "Insufficient opening stock"
                if demand_qty > 800:
                    root_cause = "Demand spike"
                elif not lt:
                    root_cause = "Missing supplier information (Lead time missing)"
                elif sku and sku.criticality == "Critical":
                    root_cause = "Supplier capacity shortage / High criticality constraint"

                # Unambiguous Severity Classification (Critical takes absolute precedence)
                if proj_avail < 0:
                    severity = "Critical"
                elif shortage_qty > 500.0 or (sku and sku.criticality == "Critical" and proj_avail <= safety * 0.5):
                    severity = "High"
                elif shortage_qty <= 10.0:
                    severity = "Low"
                else:
                    severity = "Medium"

                sku_crit = sku.criticality if sku and sku.criticality in ["Critical", "High", "Medium", "Low"] else "Medium"
                priority_score = calculate_priority_score(severity, sku_crit, shortage_qty)

                shortage_id = f"SHORT-{d.sku_id}-{d.location_id}-{d.week_start}"

                shortages_data.append({
                    "shortage_id": shortage_id,
                    "sku_id": d.sku_id,
                    "location_id": d.location_id,
                    "week_start": d.week_start,
                    "demand_quantity": demand_qty,
                    "projected_available": proj_avail,
                    "shortage_quantity": shortage_qty,
                    "severity": severity,
                    "root_cause": root_cause,
                    "priority_score": priority_score,
                    "status": "Open"
                })

        # Deterministic sorting: priority score desc, shortage quantity desc, ids asc
        shortages_data.sort(key=lambda x: (-x["priority_score"], -x["shortage_quantity"], x["sku_id"], x["location_id"], x["week_start"]))

        # Transaction-safe update / insert using savepoint
        with db.begin_nested():
            db.query(Shortage).delete()
            for s_dict in shortages_data:
                shortage = Shortage(**s_dict)
                db.add(shortage)
        db.commit()

        return len(shortages_data)
    except Exception as e:
        db.rollback()
        raise e
