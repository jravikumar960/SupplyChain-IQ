from sqlalchemy.orm import Session
from backend.app.models.models import Shortage, SupplierCapacity, LeadTime, SKUSubstitute, MitigationOption, SKU
from backend.app.services.supplier_engine import check_supplier_feasibility

def generate_mitigations_for_shortages(db: Session):
    db.query(MitigationOption).delete()
    db.commit()

    shortages = db.query(Shortage).all()
    count = 0

    for s in shortages:
        sku = db.query(SKU.sku_id, SKU.unit_cost).filter(SKU.sku_id == s.sku_id).first()
        unit_cost = sku.unit_cost if sku else 50.0

        # Option 1: Existing or Alternative Supplier PO
        capacities = db.query(SupplierCapacity).filter(SupplierCapacity.sku_id == s.sku_id).all()
        for cap in capacities[:2]: # top 2 suppliers
            feasibility = check_supplier_feasibility(db, cap.supplier_id, s.sku_id, s.shortage_quantity)
            status = "Feasible" if feasibility["feasible"] else "Infeasible"
            score = 90.0 if status == "Feasible" else 30.0

            mit = MitigationOption(
                mitigation_id=f"MIT-{s.shortage_id}-{cap.supplier_id}",
                shortage_id=s.shortage_id,
                mitigation_type="SupplierPO",
                proposed_quantity=s.shortage_quantity,
                estimated_cost=round(s.shortage_quantity * unit_cost * 1.05, 2),
                expected_arrival_date="2026-03-20",
                service_impact="High" if s.severity == "Critical" else "Medium",
                feasibility_status=status,
                recommendation_score=score,
                is_approved=False
            )
            db.add(mit)
            count += 1

        # Option 2: Approved Substitute SKU
        substitutes = db.query(SKUSubstitute).filter(SKUSubstitute.sku_id == s.sku_id).all()
        for sub in substitutes:
            # Rule: NEVER recommend an unapproved substitute
            if not sub.is_approved:
                status = "Infeasible"
                score = 0.0
                notes = "Blocked: Substitute SKU is unapproved by engineering."
            else:
                status = "Feasible"
                score = 85.0
                notes = "Approved substitute available."

            mit = MitigationOption(
                mitigation_id=f"MIT-{s.shortage_id}-SUB-{sub.substitute_sku_id}",
                shortage_id=s.shortage_id,
                mitigation_type="SubstituteSKU",
                proposed_quantity=s.shortage_quantity,
                estimated_cost=round(s.shortage_quantity * unit_cost * 0.9, 2),
                expected_arrival_date="2026-03-10",
                service_impact="Medium",
                feasibility_status=status,
                recommendation_score=score,
                is_approved=False
            )
            db.add(mit)
            count += 1

        # Option 3: Production Increase
        mit_prod = MitigationOption(
            mitigation_id=f"MIT-{s.shortage_id}-PROD",
            shortage_id=s.shortage_id,
            mitigation_type="ProductionIncrease",
            proposed_quantity=s.shortage_quantity,
            estimated_cost=round(s.shortage_quantity * unit_cost * 0.8, 2),
            expected_arrival_date="2026-03-25",
            service_impact="High",
            feasibility_status="Feasible",
            recommendation_score=75.0,
            is_approved=False
        )
        db.add(mit_prod)
        count += 1

    db.commit()
    return count
