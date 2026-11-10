from sqlalchemy.orm import Session
from backend.app.models.models import Inventory, PurchaseOrder, ProductionPlan, ForecastDemand

def calculate_projected_inventory(db: Session, sku_id: str, location_id: str, week_start: str) -> dict:
    # 1. Opening on-hand inventory
    inv = db.query(Inventory).filter(Inventory.sku_id == sku_id, Inventory.location_id == location_id).first()
    opening_on_hand = inv.on_hand_quantity if inv else 0.0
    reserved = inv.reserved_quantity if inv else 0.0
    safety = inv.safety_stock if inv else 0.0
    available_opening = max(0.0, opening_on_hand - reserved)

    # 2. Valid Inbound Receipts (excluding duplicate POs for Anomaly A)
    valid_pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.sku_id == sku_id,
        PurchaseOrder.location_id == location_id,
        PurchaseOrder.is_duplicate == False,
        PurchaseOrder.status.in_(["Pending", "Received"])
    ).all()
    inbound_receipts = sum(po.received_quantity if po.status == "Received" else po.ordered_quantity for po in valid_pos)

    # 3. Planned Production Receipts
    prod_plans = db.query(ProductionPlan).filter(
        ProductionPlan.sku_id == sku_id,
        ProductionPlan.location_id == location_id,
        ProductionPlan.status.in_(["Planned", "InProgress"])
    ).all()
    production_receipts = sum(p.planned_quantity for p in prod_plans)

    # 4. Forecast Demand for the week
    demand_rec = db.query(ForecastDemand).filter(
        ForecastDemand.sku_id == sku_id,
        ForecastDemand.location_id == location_id,
        ForecastDemand.week_start == week_start
    ).first()
    demand_qty = demand_rec.forecast_quantity if demand_rec else 0.0

    # Projected Available Balance
    projected_available = available_opening + inbound_receipts + production_receipts - demand_qty

    return {
        "sku_id": sku_id,
        "location_id": location_id,
        "week_start": week_start,
        "opening_available": available_opening,
        "inbound_receipts": inbound_receipts,
        "production_receipts": production_receipts,
        "demand_quantity": demand_qty,
        "safety_stock": safety,
        "projected_available": round(projected_available, 2)
    }
