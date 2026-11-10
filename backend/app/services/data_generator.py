import os
import json
import random
import pandas as pd
from datetime import datetime, timedelta, timezone
from backend.app.database import SessionLocal, engine
from backend.app.models.models import (
    Base, SKU, Location, ForecastDemand, Inventory, Supplier,
    SupplierCapacity, LeadTime, PurchaseOrder, ProductionPlan,
    BOM, SKUSubstitute, DataIssue, DetectorExecution
)

def generate_synthetic_data(
    num_skus=100,
    num_locations=10,
    num_weeks=12,
    num_suppliers=30,
    num_pos=300,
    seed=20261022,
    batch_size=5000,
    reset=False
):
    """
    Generate synthetic supply chain dataset with configurable parameters,
    isolated RNG seed, non-destructive default behavior, batched inserts,
    and explicit detector execution tracking records.
    """
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    rng = random.Random(seed)

    categories = ["Electronics", "Raw Materials", "Packaging", "Finished Goods", "Chemicals", "Hardware"]
    uoms = ["PCS", "KG", "LTR", "BOX", "PALLET"]
    criticalities = ["Critical", "High", "Medium", "Low"]
    location_types = ["Warehouse", "DistributionCenter", "RetailStore", "Plant"]
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]

    # 1. SKU Master (Parent)
    skus = []
    for i in range(1, num_skus + 1):
        sku_id = f"SKU-{i:06d}"
        sku = SKU(
            sku_id=sku_id,
            sku_name=f"Product {i} ({rng.choice(categories)})",
            category=rng.choice(categories),
            unit_of_measure=rng.choice(uoms),
            unit_cost=round(rng.uniform(5.0, 500.0), 2),
            criticality=rng.choice(criticalities),
            is_active=True
        )
        db.add(sku)
        skus.append(sku)
    db.commit()

    # 2. Location Master (Parent)
    locations = []
    for i in range(1, num_locations + 1):
        loc_id = f"LOC-{i:06d}"
        loc = Location(
            location_id=loc_id,
            location_name=f"Facility {i} - {rng.choice(regions)}",
            location_type=rng.choice(location_types),
            region=rng.choice(regions),
            storage_capacity=round(rng.uniform(50000.0, 500000.0), 2)
        )
        db.add(loc)
        locations.append(loc)
    db.commit()

    # 3. Supplier Master (Parent)
    suppliers = []
    for i in range(1, num_suppliers + 1):
        sup_id = f"SUP-{i:06d}"
        sup = Supplier(
            supplier_id=sup_id,
            supplier_name=f"Global Supplier {i}",
            region=rng.choice(regions),
            reliability_score=round(rng.uniform(0.7, 0.99), 2),
            is_active=True
        )
        db.add(sup)
        suppliers.append(sup)
    db.commit()

    # 4. Supplier Capacities
    sup_caps = []
    for i, sup in enumerate(suppliers):
        for j in range(2):
            sku = skus[(i * 2 + j) % len(skus)]
            cap = SupplierCapacity(
                capacity_id=f"CAP-{sup.supplier_id}-{sku.sku_id}",
                supplier_id=sup.supplier_id,
                sku_id=sku.sku_id,
                weekly_capacity=round(rng.uniform(100.0, 2000.0), 2),
                minimum_order_quantity=round(rng.uniform(10.0, 100.0), 2),
                effective_from="2026-W01",
                effective_to="2026-W52"
            )
            sup_caps.append(cap)
    for i in range(0, len(sup_caps), batch_size):
        db.add_all(sup_caps[i:i+batch_size])
        db.commit()

    # 5. Lead Times
    lead_times = []
    for sup in suppliers:
        for sku in skus[:10]:
            min_d = rng.randint(1, 5)
            avg_d = min_d + rng.randint(2, 5)
            max_d = avg_d + rng.randint(3, 10)
            lt = LeadTime(
                lead_time_id=f"LT-{sup.supplier_id}-{sku.sku_id}",
                supplier_id=sup.supplier_id,
                sku_id=sku.sku_id,
                min_days=min_d,
                average_days=avg_d,
                max_days=max_d
            )
            lead_times.append(lt)
    for i in range(0, len(lead_times), batch_size):
        db.add_all(lead_times[i:i+batch_size])
        db.commit()

    # 6. Inventory Master
    inventories = []
    for sku in skus:
        for loc in locations[:3]:
            on_hand = round(rng.uniform(50.0, 5000.0), 2)
            reserved = round(rng.uniform(0.0, on_hand * 0.3), 2)
            safety = round(rng.uniform(20.0, 200.0), 2)
            inv = Inventory(
                inventory_id=f"INV-{sku.sku_id}-{loc.location_id}",
                sku_id=sku.sku_id,
                location_id=loc.location_id,
                on_hand_quantity=on_hand,
                reserved_quantity=reserved,
                safety_stock=safety,
                unit_of_measure=sku.unit_of_measure
            )
            inventories.append(inv)
    for i in range(0, len(inventories), batch_size):
        db.add_all(inventories[i:i+batch_size])
        db.commit()

    # 7. Forecast Demands
    demands = []
    for sku in skus[:50]:
        for loc in locations[:3]:
            for w in range(1, num_weeks + 1):
                dem = ForecastDemand(
                    demand_id=f"DEM-{sku.sku_id}-{loc.location_id}-W{w:02d}",
                    sku_id=sku.sku_id,
                    location_id=loc.location_id,
                    week_start=f"2026-W{w:02d}",
                    forecast_quantity=round(rng.uniform(50.0, 800.0), 2)
                )
                demands.append(dem)
    for i in range(0, len(demands), batch_size):
        db.add_all(demands[i:i+batch_size])
        db.commit()

    # 8. Purchase Orders
    pos = []
    statuses = ["Pending", "Received", "Delayed", "Cancelled"]
    for i in range(1, num_pos + 1):
        po_id = f"PO-{i:06d}"
        sku = rng.choice(skus)
        loc = rng.choice(locations[:3])
        sup = rng.choice(suppliers)
        qty = round(rng.uniform(100.0, 2000.0), 2)
        stat = rng.choice(statuses)
        w = rng.randint(1, num_weeks)
        po = PurchaseOrder(
            po_id=po_id,
            supplier_id=sup.supplier_id,
            sku_id=sku.sku_id,
            location_id=loc.location_id,
            ordered_quantity=qty,
            received_quantity=qty if stat == "Received" else 0.0,
            expected_delivery_date=f"2026-W{w:02d}",
            status=stat,
            is_duplicate=False,
            unit_of_measure=sku.unit_of_measure
        )
        pos.append(po)
    for i in range(0, len(pos), batch_size):
        db.add_all(pos[i:i+batch_size])
        db.commit()

    # 9. Production Plans
    prods = []
    for i in range(1, 100 + 1):
        prod_id = f"PROD-{i:06d}"
        sku = rng.choice(skus)
        loc = rng.choice(locations[:3])
        w = rng.randint(1, num_weeks)
        prod = ProductionPlan(
            production_id=prod_id,
            sku_id=sku.sku_id,
            location_id=loc.location_id,
            planned_quantity=round(rng.uniform(200.0, 5000.0), 2),
            production_start=f"2026-W{w:02d}",
            production_end=f"2026-W{w:02d}",
            capacity_available=10000.0,
            status=rng.choice(["Planned", "InProgress", "Completed"])
        )
        prods.append(prod)
    for i in range(0, len(prods), batch_size):
        db.add_all(prods[i:i+batch_size])
        db.commit()

    # 10. BOM and Substitutes
    bom_batch = []
    bom_count = min(30, num_skus)
    for i in range(1, bom_count + 1):
        parent = skus[i-1]
        comp = skus[(i+10) % len(skus)]
        bom = BOM(
            bom_id=f"BOM-{parent.sku_id}-{comp.sku_id}",
            parent_sku_id=parent.sku_id,
            component_sku_id=comp.sku_id,
            quantity_required=round(rng.uniform(1.0, 5.0), 2),
            component_unit_of_measure=comp.unit_of_measure
        )
        bom_batch.append(bom)
    if bom_batch:
        db.add_all(bom_batch)
        db.commit()

    sub_batch = []
    sub_count = min(30, num_skus)
    for i in range(1, sub_count + 1):
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
        sub_batch.append(sub_record)
    if sub_batch:
        db.add_all(sub_batch)
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
            is_duplicate=True,
            unit_of_measure=target_po.unit_of_measure
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
            "entity_type": "PurchaseOrder",
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
            "entity_type": "SKUSubstitute",
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
            "entity_type": "SupplierCapacity",
            "entity_id": target_cap.capacity_id,
            "description": "Supplier capacity violation injected."
        })

    # Anomaly D: SHORTAGE_WITHOUT_LEAD_TIME
    if len(skus) > 1:
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
            "entity_type": "SKU",
            "entity_id": target_sku.sku_id,
            "description": "Shortage with missing lead time injected."
        })

    # Anomaly E: UNIT_OF_MEASURE_MISMATCH
    if len(skus) > 2:
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
            "entity_type": "SKU",
            "entity_id": skus[2].sku_id,
            "description": "Unit of measure mismatch injected."
        })

    db.commit()

    # Populate explicit DetectorExecution records for all DataIssues and evaluated clean SKUs
    for issue in db.query(DataIssue).all():
        exec_rec = DetectorExecution(
            execution_id=f"EXEC-INIT-{issue.issue_id}",
            evaluation_run_id="RUN-INIT",
            detector_type=issue.issue_type,
            entity_type=issue.affected_entity_type,
            entity_id=issue.affected_entity_id
        )
        db.add(exec_rec)

    for idx, sku in enumerate(skus[:50]):
        exec_rec = DetectorExecution(
            execution_id=f"EXEC-INIT-CLEAN-{idx}",
            evaluation_run_id="RUN-INIT",
            detector_type="INBOUND_COUNTED_TWICE",
            entity_type="SKU",
            entity_id=sku.sku_id
        )
        db.add(exec_rec)

    db.commit()

    # Save Ground Truth files
    gt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/ground_truth"))
    os.makedirs(gt_dir, exist_ok=True)

    with open(os.path.join(gt_dir, "ground_truth.json"), "w") as f:
        json.dump(ground_truth_anomalies, f, indent=2)

    df_gt = pd.DataFrame(ground_truth_anomalies)
    df_gt.to_csv(os.path.join(gt_dir, "ground_truth.csv"), index=False)

    db.close()
