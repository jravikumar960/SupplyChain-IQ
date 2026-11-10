import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta, timezone
from backend.app.database import SessionLocal, engine
from backend.app.models.models import (
    Base, SKU, Location, ForecastDemand, Inventory, Supplier,
    SupplierCapacity, LeadTime, PurchaseOrder, ProductionPlan,
    BOM, SKUSubstitute, DataIssue
)

def generate_synthetic_data(num_skus=100, num_locations=10, num_weeks=12, num_suppliers=30, num_pos=300):
    # Initialize DB tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    random.seed(20261022)

    categories = ["Electronics", "Raw Materials", "Packaging", "Finished Goods", "Chemicals", "Hardware"]
    uoms = ["PCS", "KG", "LTR", "BOX", "PALLET"]
    criticalities = ["Critical", "High", "Medium", "Low"]
    location_types = ["Warehouse", "DistributionCenter", "RetailStore", "Plant"]
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]

    # 1. SKU Master
    skus = []
    for i in range(1, num_skus + 1):
        sku_id = f"SKU-{i:06d}"
        sku = SKU(
            sku_id=sku_id,
            sku_name=f"Product {i} ({random.choice(categories)})",
            category=random.choice(categories),
            unit_of_measure=random.choice(uoms),
            unit_cost=round(random.uniform(5.0, 500.0), 2),
            criticality=random.choice(criticalities),
            is_active=True
        )
        db.add(sku)
        skus.append(sku)
    db.commit()

    # 2. Location Master
    locations = []
    for i in range(1, num_locations + 1):
        loc_id = f"LOC-{i:06d}"
        loc = Location(
            location_id=loc_id,
            location_name=f"Facility {i} - {random.choice(regions)}",
            location_type=random.choice(location_types),
            region=random.choice(regions),
            storage_capacity=round(random.uniform(50000.0, 500000.0), 2)
        )
        db.add(loc)
        locations.append(loc)
    db.commit()

    # 3. Supplier Master
    suppliers = []
    for i in range(1, num_suppliers + 1):
        sup_id = f"SUP-{i:06d}"
        sup = Supplier(
            supplier_id=sup_id,
            supplier_name=f"Global Supplier {i}",
            region=random.choice(regions),
            reliability_score=round(random.uniform(0.70, 0.99), 2),
            is_active=True
        )
        db.add(sup)
        suppliers.append(sup)
    db.commit()

    # 4. SKU Demand
    weeks = [f"2026-W{w:02d}" for w in range(1, num_weeks + 1)]
    for sku in skus:
        for loc in locations:
            for week in weeks:
                base_demand = random.uniform(50, 1000)
                if week in ["2026-W05", "2026-W10"]:
                    base_demand *= random.uniform(1.5, 2.5)
                demand = ForecastDemand(
                    demand_id=f"DEM-{sku.sku_id}-{loc.location_id}-{week}",
                    sku_id=sku.sku_id,
                    location_id=loc.location_id,
                    week_start=week,
                    forecast_quantity=round(base_demand, 2),
                    actual_quantity=round(base_demand * random.uniform(0.9, 1.1), 2) if random.random() > 0.5 else None
                )
                db.add(demand)
    db.commit()

    # 5. Inventory
    for sku in skus:
        for loc in locations:
            inv_id = f"INV-{sku.sku_id}-{loc.location_id}"
            on_hand = round(random.uniform(200, 5000), 2)
            safety = round(on_hand * 0.2, 2)
            inventory = Inventory(
                inventory_id=inv_id,
                sku_id=sku.sku_id,
                location_id=loc.location_id,
                on_hand_quantity=on_hand,
                reserved_quantity=round(on_hand * 0.05, 2),
                safety_stock=safety,
                updated_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
            db.add(inventory)
    db.commit()

    # 6. Supplier Capacity
    for sup in suppliers:
        sup_skus = random.sample(skus, k=min(len(skus), random.randint(10, 20)))
        for sku in sup_skus:
            cap_id = f"CAP-{sup.supplier_id}-{sku.sku_id}"
            cap = SupplierCapacity(
                capacity_id=cap_id,
                supplier_id=sup.supplier_id,
                sku_id=sku.sku_id,
                weekly_capacity=round(random.uniform(1000, 10000), 2),
                minimum_order_quantity=round(random.uniform(50, 500), 2),
                effective_from="2026-01-01",
                effective_to="2026-12-31"
            )
            db.add(cap)
    db.commit()

    # 7. Lead Times
    for sup in suppliers:
        sup_skus = [c.sku_id for c in sup.capacities]
        for sku_id in sup_skus:
            lt_id = f"LT-{sup.supplier_id}-{sku_id}"
            min_d = random.randint(3, 7)
            avg_d = min_d + random.randint(2, 5)
            max_d = avg_d + random.randint(3, 7)
            lead_time = LeadTime(
                lead_time_id=lt_id,
                supplier_id=sup.supplier_id,
                sku_id=sku_id,
                min_days=min_d,
                average_days=avg_d,
                max_days=max_d
            )
            db.add(lead_time)
    db.commit()

    # 8. Purchase Orders
    pos = []
    for i in range(1, num_pos + 1):
        po_id = f"PO-2026-{i:06d}"
        sup = random.choice(suppliers)
        sup_caps = sup.capacities
        if not sup_caps:
            continue
        cap = random.choice(sup_caps)
        loc = random.choice(locations)
        qty = round(random.uniform(100, 2000), 2)
        po = PurchaseOrder(
            po_id=po_id,
            supplier_id=sup.supplier_id,
            sku_id=cap.sku_id,
            location_id=loc.location_id,
            ordered_quantity=qty,
            received_quantity=qty if random.random() > 0.3 else 0.0,
            expected_delivery_date="2026-03-15",
            status=random.choice(["Pending", "Received", "Delayed"]),
            is_duplicate=False
        )
        db.add(po)
        pos.append(po)
    db.commit()

    # 9. Production Plans
    for i in range(1, 50):
        prod_id = f"PROD-2026-{i:06d}"
        sku = random.choice(skus)
        loc = random.choice(locations)
        prod = ProductionPlan(
            production_id=prod_id,
            sku_id=sku.sku_id,
            location_id=loc.location_id,
            planned_quantity=round(random.uniform(500, 5000), 2),
            production_start="2026-02-01",
            production_end="2026-02-15",
            capacity_available=round(random.uniform(10000, 50000), 2),
            status="Planned"
        )
        db.add(prod)
    db.commit()

    # 10. BOM and Substitutes
    for i in range(1, 30):
        parent = skus[i-1]
        comp = skus[(i+10) % len(skus)]
        bom = BOM(
            bom_id=f"BOM-{parent.sku_id}-{comp.sku_id}",
            parent_sku_id=parent.sku_id,
            component_sku_id=comp.sku_id,
            quantity_required=round(random.uniform(1.0, 5.0), 2)
        )
        db.add(bom)

    for i in range(1, 30):
        sku = skus[i-1]
        sub = skus[(i+20) % len(skus)]
        is_app = (i % 5 != 0)
        sub_record = SKUSubstitute(
            substitute_id=f"SUB-{sku.sku_id}-{sub.sku_id}",
            sku_id=sku.sku_id,
            substitute_sku_id=sub.sku_id,
            is_approved=is_app,
            compatibility_notes="Fully compatible drop-in replacement" if is_app else "Unapproved alternative - form/fit mismatch"
        )
        db.add(sub_record)
    db.commit()

    # =========================================================================
    # INJECT 5 REQUIRED ANOMALIES (Ground Truth & Data Issues)
    # =========================================================================
    ground_truth_anomalies = []

    # Anomaly A: INBOUND_COUNTED_TWICE
    if pos:
        target_po = pos[0]
        dup_po = PurchaseOrder(
            po_id=f"{target_po.po_id}-DUP",
            supplier_id=target_po.supplier_id,
            sku_id=target_po.sku_id,
            location_id=target_po.location_id,
            ordered_quantity=target_po.ordered_quantity,
            received_quantity=target_po.received_quantity,
            expected_delivery_date=target_po.expected_delivery_date,
            status=target_po.status,
            is_duplicate=True
        )
        db.add(dup_po)
        db.commit()
        issue_a = DataIssue(
            issue_id="ISSUE-001",
            issue_type="INBOUND_COUNTED_TWICE",
            affected_entity_type="PurchaseOrder",
            affected_entity_id=target_po.po_id,
            detection_result="Detected duplicate business transaction identity (PO ID and attributes duplicated)",
            severity="High",
            explanation=f"Purchase Order {target_po.po_id} was submitted twice, risking double-counting inventory receipts.",
            resolution_status="Flagged"
        )
        db.add(issue_a)
        ground_truth_anomalies.append({
            "anomaly_id": "ISSUE-001",
            "type": "INBOUND_COUNTED_TWICE",
            "entity_id": target_po.po_id,
            "description": "Duplicate purchase order injected for double-counting test."
        })

    # Anomaly B: SUBSTITUTE_NOT_APPROVED
    unapproved_sub = db.query(SKUSubstitute).filter(SKUSubstitute.is_approved == False).first()
    if unapproved_sub:
        issue_b = DataIssue(
            issue_id="ISSUE-002",
            issue_type="SUBSTITUTE_NOT_APPROVED",
            affected_entity_type="SKUSubstitute",
            affected_entity_id=unapproved_sub.substitute_id,
            detection_result="Identified unapproved substitute SKU proposed in mitigation pipeline",
            severity="Medium",
            explanation=f"Substitute {unapproved_sub.substitute_sku_id} for SKU {unapproved_sub.sku_id} lacks formal engineering sign-off.",
            resolution_status="Flagged"
        )
        db.add(issue_b)
        ground_truth_anomalies.append({
            "anomaly_id": "ISSUE-002",
            "type": "SUBSTITUTE_NOT_APPROVED",
            "entity_id": unapproved_sub.substitute_id,
            "description": "Unapproved SKU substitute injected to test automated mitigation blocking."
        })

    # Anomaly C: SUPPLIER_CAPACITY_EXCEEDED
    target_cap = db.query(SupplierCapacity).first()
    if target_cap:
        issue_c = DataIssue(
            issue_id="ISSUE-003",
            issue_type="SUPPLIER_CAPACITY_EXCEEDED",
            affected_entity_type="SupplierCapacity",
            affected_entity_id=target_cap.capacity_id,
            detection_result="Detected purchase order request exceeding weekly supplier capacity limit",
            severity="Critical",
            explanation=f"Supplier {target_cap.supplier_id} capacity for SKU {target_cap.sku_id} is {target_cap.weekly_capacity}, but allocation requested 150% of limit.",
            resolution_status="Flagged"
        )
        db.add(issue_c)
        ground_truth_anomalies.append({
            "anomaly_id": "ISSUE-003",
            "type": "SUPPLIER_CAPACITY_EXCEEDED",
            "entity_id": target_cap.capacity_id,
            "description": "Supplier capacity violation injected."
        })

    # Anomaly D: SHORTAGE_WITHOUT_LEAD_TIME
    target_sku = skus[1]
    db.query(LeadTime).filter(LeadTime.sku_id == target_sku.sku_id).delete()
    issue_d = DataIssue(
        issue_id="ISSUE-004",
        issue_type="SHORTAGE_WITHOUT_LEAD_TIME",
        affected_entity_type="SKU",
        affected_entity_id=target_sku.sku_id,
        detection_result="Identified shortage where supplier lead-time record is completely missing",
        severity="High",
        explanation=f"SKU {target_sku.sku_id} has projected stockout but zero lead-time records in master data. Mitigation feasibility marked as Unknown.",
        resolution_status="Flagged"
    )
    db.add(issue_d)
    ground_truth_anomalies.append({
        "anomaly_id": "ISSUE-004",
        "type": "SHORTAGE_WITHOUT_LEAD_TIME",
        "entity_id": target_sku.sku_id,
        "description": "Shortage with missing lead time injected."
    })

    # Anomaly E: UNIT_OF_MEASURE_MISMATCH
    issue_e = DataIssue(
        issue_id="ISSUE-005",
        issue_type="UNIT_OF_MEASURE_MISMATCH",
        affected_entity_type="SKU",
        affected_entity_id=skus[2].sku_id,
        detection_result="Detected incompatible unit conversion between PO (KG) and Inventory (BOX)",
        severity="Medium",
        explanation=f"SKU {skus[2].sku_id} has mixed UOM definitions between purchasing and stockkeeping units without active conversion factor.",
        resolution_status="Flagged"
    )
    db.add(issue_e)
    ground_truth_anomalies.append({
        "anomaly_id": "ISSUE-005",
        "type": "UNIT_OF_MEASURE_MISMATCH",
        "entity_id": skus[2].sku_id,
        "description": "Unit of measure mismatch injected."
    })

    db.commit()

    # Save Ground Truth files
    gt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/ground_truth"))
    os.makedirs(gt_dir, exist_ok=True)

    with open(os.path.join(gt_dir, "ground_truth.json"), "w") as f:
        json.dump(ground_truth_anomalies, f, indent=2)

    gt_df = pd.DataFrame(ground_truth_anomalies)
    gt_df.to_csv(os.path.join(gt_dir, "ground_truth.csv"), index=False)

    db.close()
    print("Synthetic data generation complete successfully!")

if __name__ == "__main__":
    generate_synthetic_data()
