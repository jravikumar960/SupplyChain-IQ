from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.models.models import Inventory, PurchaseOrder, ProductionPlan, ForecastDemand

def date_to_week_str(date_str: str) -> str:
    if not date_str:
        return ""
    date_str = str(date_str).strip()
    if "-W" in date_str.upper():
        return date_str.upper()
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        iso_year, iso_week, _ = dt.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    except ValueError:
        return date_str.upper()

def calculate_projected_inventory(db: Session, sku_id: str, location_id: str, week_start: str) -> dict:
    # Get all weeks sorted chronologically for this SKU and location
    demands = db.query(ForecastDemand).filter(
        ForecastDemand.sku_id == sku_id,
        ForecastDemand.location_id == location_id
    ).order_by(ForecastDemand.week_start).all()

    weeks = [d.week_start for d in demands]
    if not weeks:
        weeks = ["2026-W01"]
    else:
        weeks = sorted(list(set(weeks)))

    # Ensure week_start is in weeks, or add and sort
    if week_start not in weeks:
        weeks.append(week_start)
        weeks = sorted(list(set(weeks)))

    # Initial opening inventory from Inventory master table
    inv = db.query(Inventory).filter(Inventory.sku_id == sku_id, Inventory.location_id == location_id).first()
    opening_on_hand = inv.on_hand_quantity if inv else 0.0
    reserved = inv.reserved_quantity if inv else 0.0
    safety = inv.safety_stock if inv else 0.0
    current_opening = max(0.0, opening_on_hand - reserved)

    # Fetch all valid POs and Production plans for this SKU/location
    all_pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.sku_id == sku_id,
        PurchaseOrder.location_id == location_id,
        PurchaseOrder.is_duplicate == False,
        PurchaseOrder.status.in_(["Pending", "Received"])
    ).all()

    all_prods = db.query(ProductionPlan).filter(
        ProductionPlan.sku_id == sku_id,
        ProductionPlan.location_id == location_id,
        ProductionPlan.status.in_(["Planned", "InProgress"])
    ).all()

    target_result = None

    for w in weeks:
        # 1. Inbound PO receipts expected in week w (matched via date conversion to ISO week)
        week_inbound = sum(
            po.received_quantity if po.status == "Received" else po.ordered_quantity
            for po in all_pos
            if date_to_week_str(str(po.expected_delivery_date)) == w
        )

        # 2. Production receipts expected in week w (matched via production_end or start converted to ISO week)
        week_prod = sum(
            p.planned_quantity
            for p in all_prods
            if date_to_week_str(str(p.production_end)) == w or date_to_week_str(str(p.production_start)) == w
        )

        # 3. Demand in week w
        demand_rec = db.query(ForecastDemand).filter(
            ForecastDemand.sku_id == sku_id,
            ForecastDemand.location_id == location_id,
            ForecastDemand.week_start == w
        ).first()
        demand_qty = demand_rec.forecast_quantity if demand_rec else 0.0

        # Closing inventory for week w = Opening + Inbound + Production - Demand
        closing = current_opening + week_inbound + week_prod - demand_qty

        res = {
            "sku_id": sku_id,
            "location_id": location_id,
            "week_start": w,
            "opening_available": round(current_opening, 2),
            "inbound_receipts": round(week_inbound, 2),
            "production_receipts": round(week_prod, 2),
            "demand_quantity": round(demand_qty, 2),
            "safety_stock": round(safety, 2),
            "projected_available": round(closing, 2)
        }

        if w == week_start:
            target_result = res
            break

        # Sequential carry-over to next week's opening inventory (carrying over negative balances as backorders/deficits)
        current_opening = closing

    if not target_result:
        target_result = {
            "sku_id": sku_id,
            "location_id": location_id,
            "week_start": week_start,
            "opening_available": round(current_opening, 2),
            "inbound_receipts": 0.0,
            "production_receipts": 0.0,
            "demand_quantity": 0.0,
            "safety_stock": round(safety, 2),
            "projected_available": round(current_opening, 2)
        }

    return target_result
