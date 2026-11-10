from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from backend.app.models.models import (
    Shortage, SupplierCapacity, LeadTime, SKUSubstitute,
    MitigationOption, SKU, Supplier, PurchaseOrder, MitigationDecision, AuditLog
)
from backend.app.services.supplier_engine import check_supplier_feasibility

def parse_iso_week_to_date(week_str: str) -> datetime:
    try:
        parts = week_str.upper().split("-W")
        year = int(parts[0])
        week = int(parts[1])
        return datetime.strptime(f"{year}-W{week:02d}-1", "%G-W%V-%u")
    except Exception:
        return datetime.now(timezone.utc).replace(tzinfo=None)

def generate_mitigations_for_shortages(db: Session, limit: int = None):
    # Clear existing mitigations
    db.query(MitigationOption).delete()
    db.commit()

    query = db.query(Shortage)
    if limit:
        query = query.limit(limit)
    shortages = query.all()

    # Pre-fetch master data into memory dictionaries for O(1) lookup
    skus_dict = {s.sku_id: s for s in db.query(SKU).all()}
    suppliers_dict = {sup.supplier_id: sup for sup in db.query(Supplier).all()}

    capacities_list = db.query(SupplierCapacity).all()
    capacities_by_sku = {}
    for c in capacities_list:
        capacities_by_sku.setdefault(c.sku_id, []).append(c)

    lead_times_list = db.query(LeadTime).all()
    lead_times_by_sku = {}
    for lt in lead_times_list:
        lead_times_by_sku.setdefault((lt.supplier_id, lt.sku_id), lt)

    substitutes_list = db.query(SKUSubstitute).all()
    substitutes_by_sku = {}
    for sub in substitutes_list:
        substitutes_by_sku.setdefault(sub.sku_id, []).append(sub)

    mitigations_to_add = []
    count = 0

    for s in shortages:
        sku = skus_dict.get(s.sku_id)
        unit_cost = sku.unit_cost if sku else 50.0
        shortage_date = parse_iso_week_to_date(s.week_start)

        # 1. Supplier PO Options
        sku_caps = capacities_by_sku.get(s.sku_id, [])
        for cap in sku_caps:
            supplier = suppliers_dict.get(cap.supplier_id)
            if not supplier or not supplier.is_active:
                continue

            lt = lead_times_by_sku.get((cap.supplier_id, s.sku_id))
            avg_lead_days = lt.average_days if lt else 14
            expected_arrival_str = (shortage_date - timedelta(days=max(0, 7 - avg_lead_days))).strftime("%Y-%m-%d")

            req_qty = max(s.shortage_quantity, cap.minimum_order_quantity)

            # Check capacity & MOQ rules in memory
            capacity_feasible = req_qty <= cap.weekly_capacity
            moq_feasible = req_qty >= cap.minimum_order_quantity
            lead_time_feasible = avg_lead_days <= 21

            reasons = []
            if not capacity_feasible:
                reasons.append(f"Requested quantity ({req_qty:.2f}) exceeds weekly supplier capacity ({cap.weekly_capacity:.2f})")
            if not moq_feasible:
                reasons.append(f"Requested quantity ({req_qty:.2f}) is below Minimum Order Quantity ({cap.minimum_order_quantity:.2f})")
            if not lead_time_feasible:
                reasons.append(f"Average lead time ({avg_lead_days} days) exceeds maximum threshold of 21 days")

            if not reasons:
                feasibility_status = "Feasible"
                feasibility_explanation = f"Supplier {cap.supplier_id} ({supplier.supplier_name}) meets weekly capacity ({cap.weekly_capacity:.2f}), MOQ ({cap.minimum_order_quantity:.2f}), and lead time ({avg_lead_days} days) constraints."
                reliability = supplier.reliability_score
                lead_score = max(0.0, 15.0 - (avg_lead_days / 2.0))
                score = round(70.0 + (reliability * 15.0) + lead_score, 2)
            else:
                feasibility_status = "Infeasible"
                feasibility_explanation = f"Supplier {cap.supplier_id} ({supplier.supplier_name}) infeasible: {'; '.join(reasons)}."
                score = 15.0

            est_cost = round(req_qty * unit_cost, 2)

            mitigations_to_add.append(MitigationOption(
                mitigation_id=f"MIT-{s.shortage_id}-{cap.supplier_id}",
                shortage_id=s.shortage_id,
                mitigation_type="SupplierPO",
                proposed_quantity=req_qty,
                estimated_cost=est_cost,
                expected_arrival_date=expected_arrival_str,
                service_impact="High" if s.severity == "Critical" else "Medium",
                feasibility_status=feasibility_status,
                feasibility_explanation=feasibility_explanation,
                supplier_id=cap.supplier_id,
                recommendation_score=score,
                is_approved=False
            ))
            count += 1

        # 2. Substitute SKUs
        sku_subs = substitutes_by_sku.get(s.sku_id, [])
        for sub in sku_subs:
            if not sub.is_approved:
                feasibility_status = "Infeasible"
                feasibility_explanation = f"Substitute SKU {sub.substitute_sku_id} lacks formal engineering approval (is_approved=False)."
                score = 0.0
            else:
                feasibility_status = "Feasible"
                feasibility_explanation = f"Substitute SKU {sub.substitute_sku_id} is formally approved with compatible specifications."
                score = 80.0

            mitigations_to_add.append(MitigationOption(
                mitigation_id=f"MIT-{s.shortage_id}-SUB-{sub.substitute_sku_id}",
                shortage_id=s.shortage_id,
                mitigation_type="SubstituteSKU",
                proposed_quantity=s.shortage_quantity,
                estimated_cost=round(s.shortage_quantity * unit_cost * 0.95, 2),
                expected_arrival_date=s.week_start,
                service_impact="Medium",
                feasibility_status=feasibility_status,
                feasibility_explanation=feasibility_explanation,
                supplier_id=None,
                recommendation_score=score,
                is_approved=False
            ))
            count += 1

        # 3. Production Increase
        mitigations_to_add.append(MitigationOption(
            mitigation_id=f"MIT-{s.shortage_id}-PROD",
            shortage_id=s.shortage_id,
            mitigation_type="ProductionIncrease",
            proposed_quantity=s.shortage_quantity,
            estimated_cost=round(s.shortage_quantity * unit_cost * 0.85, 2),
            expected_arrival_date=s.week_start,
            service_impact="High",
            feasibility_status="Feasible",
            feasibility_explanation=f"Production increase of {s.shortage_quantity:.2f} units is feasible within facility production schedule and capacity.",
            supplier_id=None,
            recommendation_score=75.0,
            is_approved=False
        ))
        count += 1

    # Bulk add in transaction
    db.bulk_save_objects(mitigations_to_add)
    db.commit()
    return count
