from sqlalchemy.orm import Session
from backend.app.models.models import Supplier, SupplierCapacity, LeadTime, SKU

def check_supplier_feasibility(db: Session, supplier_id: str, sku_id: str, requested_qty: float) -> dict:
    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id, Supplier.is_active == True).first()
    if not supplier:
        return {"feasible": False, "reason": "Supplier is inactive or not found"}

    capacity = db.query(SupplierCapacity).filter(
        SupplierCapacity.supplier_id == supplier_id,
        SupplierCapacity.sku_id == sku_id
    ).first()
    if not capacity:
        return {"feasible": False, "reason": "Supplier does not supply this SKU"}

    if requested_qty > capacity.weekly_capacity:
        return {"feasible": False, "reason": f"Requested quantity exceeds weekly supplier capacity ({capacity.weekly_capacity})"}

    if requested_qty < capacity.minimum_order_quantity:
        return {"feasible": False, "reason": f"Requested quantity is below Minimum Order Quantity (MOQ: {capacity.minimum_order_quantity})"}

    lead_time = db.query(LeadTime).filter(
        LeadTime.supplier_id == supplier_id,
        LeadTime.sku_id == sku_id
    ).first()
    if not lead_time:
        return {"feasible": False, "reason": "Missing supplier lead time information (Lead time unknown)"}

    return {
        "feasible": True,
        "supplier_id": supplier_id,
        "average_lead_days": lead_time.average_days,
        "moq": capacity.minimum_order_quantity,
        "available_capacity": capacity.weekly_capacity
    }
