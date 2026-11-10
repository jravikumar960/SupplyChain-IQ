import math

def validate_uom_compatibility(po_uom: str, inv_uom: str, conversion_map: dict = None, sku_id: str = None, target_sku_id: str = None) -> tuple[bool, str, float]:
    """
    Validate unit of measure (UOM) compatibility between purchasing/inbound and inventory records.
    Ensures product-specific conversion rules (if SKU-isolated) cannot accidentally be applied to another SKU.
    Returns (is_compatible, explanation, conversion_factor).
    """
    if not po_uom or not isinstance(po_uom, str) or not po_uom.strip():
        return False, "Missing or invalid purchase UOM specification", 1.0
    if not inv_uom or not isinstance(inv_uom, str) or not inv_uom.strip():
        return False, "Missing or invalid inventory UOM specification", 1.0

    po_clean = po_uom.strip().upper()
    inv_clean = inv_uom.strip().upper()

    # Enforce SKU isolation if product-specific conversion map is restricted to a target_sku_id
    if sku_id and target_sku_id and sku_id != target_sku_id:
        return False, f"Product-specific conversion rule violation: rule for SKU '{target_sku_id}' cannot be applied to SKU '{sku_id}'", 1.0

    supported_units = {"TON", "KG", "BOX", "PCS", "L", "ML", "UNITS", "EA", "PALLET"}
    if po_clean not in supported_units or inv_clean not in supported_units:
        if not conversion_map or po_clean not in conversion_map or inv_clean not in conversion_map.get(po_clean, {}):
            return False, f"Unsupported or unknown unit of measure mismatch ('{po_uom}' vs '{inv_uom}')", 1.0

    if po_clean == inv_clean:
        return True, f"Compatible UOM: exact match ({po_uom})", 1.0

    default_conversion_map = {
        "TON": {"KG": 1000.0},
        "KG": {"TON": 0.001},
        "BOX": {"PCS": 12.0},
        "PCS": {"BOX": 1.0 / 12.0}
    }

    active_map = conversion_map if conversion_map is not None else default_conversion_map

    if not isinstance(active_map, dict):
        return False, "Malformed conversion configuration: conversion_map must be a dictionary", 1.0

    if po_clean in active_map:
        target_dict = active_map[po_clean]
        if not isinstance(target_dict, dict):
            return False, f"Malformed conversion configuration for unit '{po_clean}'", 1.0
        if inv_clean in target_dict:
            factor = target_dict[inv_clean]
            # Safety checks for factor
            if not isinstance(factor, (int, float)) or math.isnan(factor) or math.isinf(factor):
                return False, f"Invalid non-finite conversion factor for '{po_uom}' to '{inv_uom}'", 1.0
            if factor <= 0.0:
                return False, f"Invalid non-positive conversion factor ({factor}) for '{po_uom}' to '{inv_uom}'", 1.0
            return True, f"Compatible UOM via explicit conversion from {po_uom} to {inv_uom} (factor: {factor})", factor

    return False, f"Incompatible UOM mismatch: Purchase UOM '{po_uom}' cannot be reconciled with Inventory UOM '{inv_uom}' without an explicit conversion factor", 1.0
