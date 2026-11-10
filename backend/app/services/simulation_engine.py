from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import json
from backend.app.models.models import (
    SKU, Location, Inventory, ForecastDemand, PurchaseOrder, ProductionPlan, Shortage, SimulationRun, SupplierCapacity
)
from backend.app.services.inventory_engine import date_to_week_str

def run_simulation(
    db: Session,
    run_name: str,
    demand_multiplier: float = 1.0,
    supplier_capacity_multiplier: float = 1.0,
    lead_time_delay_days: int = 0
) -> SimulationRun:
    # 1. Input validation per strict requirements
    if not (1.0 <= demand_multiplier <= 2.0):
        raise ValueError("Demand multiplier must be between 1.0 and 2.0")
    if not (0.5 <= supplier_capacity_multiplier <= 1.0):
        raise ValueError("Supplier capacity multiplier must be between 0.5 and 1.0")
    if not (0 <= lead_time_delay_days <= 21):
        raise ValueError("Lead-time delay days must be between 0 and 21")

    skus = db.query(SKU).all()
    sku_costs = {sku.sku_id: sku.unit_cost for sku in skus}

    demands = db.query(ForecastDemand).all()
    if not demands:
        sim_id = f"SIM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        run = SimulationRun(
            simulation_id=sim_id,
            run_name=run_name,
            demand_multiplier=demand_multiplier,
            supplier_capacity_multiplier=supplier_capacity_multiplier,
            lead_time_delay_days=lead_time_delay_days,
            baseline_shortages_count=0,
            simulated_shortages_count=0,
            baseline_total_shortage_qty=0.0,
            simulated_total_shortage_qty=0.0,
            baseline_backorder_qty=0.0,
            simulated_backorder_qty=0.0,
            baseline_safety_deficit=0.0,
            simulated_safety_deficit=0.0,
            baseline_exposure_value=0.0,
            simulated_exposure_value=0.0,
            affected_skus_count=0,
            affected_locations_count=0,
            missing_unit_cost_count=0,
            summary_notes="Empty dataset: No forecast demand records found.",
            weekly_comparison_json=json.dumps({})
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    weeks = sorted(list(set(d.week_start for d in demands)))
    sku_loc_pairs = sorted(list(set((d.sku_id, d.location_id) for d in demands)))

    all_pos = db.query(PurchaseOrder).filter(
        PurchaseOrder.is_duplicate == False,
        PurchaseOrder.status != "Cancelled"
    ).all()

    all_prods = db.query(ProductionPlan).filter(
        ProductionPlan.status.in_(["Planned", "InProgress", "Completed"])
    ).all()

    # Pre-index purchase orders, production plans, and demands for O(1) lookup
    pos_map = {}
    for po in all_pos:
        pos_map.setdefault((po.sku_id, po.location_id), []).append(po)

    prods_map = {}
    for p in all_prods:
        prods_map.setdefault((p.sku_id, p.location_id), []).append(p)

    demand_map = {}
    for d in demands:
        demand_map.setdefault((d.sku_id, d.location_id), {})[d.week_start] = d.forecast_quantity

    inventories = db.query(Inventory).all()
    inv_map = {(inv.sku_id, inv.location_id): inv for inv in inventories}

    capacities = db.query(SupplierCapacity).all()
    cap_map = {}
    for c in capacities:
        cap_map.setdefault((c.supplier_id, c.sku_id), c.weekly_capacity)

    baseline_shortages_count = 0
    simulated_shortages_count = 0
    baseline_total_shortage_qty = 0.0
    simulated_total_shortage_qty = 0.0
    baseline_backorder_qty = 0.0
    simulated_backorder_qty = 0.0
    baseline_safety_deficit = 0.0
    simulated_safety_deficit = 0.0
    baseline_exposure = 0.0
    simulated_exposure = 0.0

    affected_skus = set()
    affected_locs = set()
    missing_cost_skus = set()

    # Helper function to run sequential projection for a given mode (baseline vs simulated)
    def run_projection(is_simulated: bool):
        nonlocal baseline_shortages_count, simulated_shortages_count
        nonlocal baseline_total_shortage_qty, simulated_total_shortage_qty
        nonlocal baseline_backorder_qty, simulated_backorder_qty
        nonlocal baseline_safety_deficit, simulated_safety_deficit
        nonlocal baseline_exposure, simulated_exposure

        shortages_count = 0
        total_shortage_qty = 0.0
        backorder_qty = 0.0
        safety_deficit = 0.0
        exposure = 0.0
        missing_costs = set()
        unvalued_qty = 0.0
        valued_qty = 0.0

        weekly_breakdown = {}

        for sku_id, location_id in sku_loc_pairs:
            inv = inv_map.get((sku_id, location_id))
            opening_on_hand = inv.on_hand_quantity if inv else 0.0
            reserved = inv.reserved_quantity if inv else 0.0
            safety = inv.safety_stock if inv else 0.0
            current_opening = max(0.0, opening_on_hand - reserved)

            sku_demands = demand_map.get((sku_id, location_id), {})
            sku_pos = pos_map.get((sku_id, location_id), [])
            sku_prods = prods_map.get((sku_id, location_id), [])

            unit_cost = sku_costs.get(sku_id, None)
            has_valid_cost = (unit_cost is not None and unit_cost > 0)
            if not has_valid_cost:
                missing_costs.add(sku_id)
                missing_cost_skus.add(sku_id)

            for w in weeks:
                # 1. Inbound receipts for week w
                week_inbound = 0.0
                for po in sku_pos:
                    delivery_date_str = str(po.expected_delivery_date)
                    if is_simulated and po.status != "Received" and lead_time_delay_days > 0:
                        try:
                            dt = datetime.strptime(delivery_date_str[:10], "%Y-%m-%d")
                            delayed_dt = dt + timedelta(days=lead_time_delay_days)
                            delivery_date_str = delayed_dt.strftime("%Y-%m-%d")
                        except Exception:
                            pass

                    po_week = date_to_week_str(delivery_date_str)
                    if po_week == w:
                        if po.status == "Received":
                            qty = po.received_quantity
                        else:
                            # Confirmed pending POs retain original ordered quantities without arbitrary reduction
                            qty = po.ordered_quantity
                        week_inbound += qty

                # 2. Production receipts for week w
                week_prod = sum(
                    p.planned_quantity for p in sku_prods
                    if date_to_week_str(str(p.production_end)) == w or date_to_week_str(str(p.production_start)) == w
                )

                # 3. Demand for week w
                base_demand = sku_demands.get(w, 0.0)
                demand_qty = base_demand * demand_multiplier if is_simulated else base_demand

                # Closing inventory
                closing = current_opening + week_inbound + week_prod - demand_qty

                # Evaluate shortage
                if closing < safety:
                    shortages_count += 1
                    s_qty = safety - closing
                    total_shortage_qty += s_qty

                    if closing < 0:
                        bo = -closing
                        backorder_qty += bo
                        sd = safety
                        safety_deficit += sd
                    else:
                        sd = safety - closing
                        safety_deficit += sd

                    if has_valid_cost:
                        exposure += s_qty * unit_cost
                        valued_qty += s_qty
                    else:
                        unvalued_qty += s_qty

                    affected_skus.add(sku_id)
                    affected_locs.add(location_id)

                    weekly_breakdown[w] = weekly_breakdown.get(w, 0) + 1

                current_opening = closing

        total_shortage_for_coverage = valued_qty + unvalued_qty
        cost_coverage_pct = round((valued_qty / total_shortage_for_coverage) * 100.0, 2) if total_shortage_for_coverage > 0 else 100.0

        if is_simulated:
            simulated_shortages_count = shortages_count
            simulated_total_shortage_qty = round(total_shortage_qty, 2)
            simulated_backorder_qty = round(backorder_qty, 2)
            simulated_safety_deficit = round(safety_deficit, 2)
            simulated_exposure = round(exposure, 2)
        else:
            baseline_shortages_count = shortages_count
            baseline_total_shortage_qty = round(total_shortage_qty, 2)
            baseline_backorder_qty = round(backorder_qty, 2)
            baseline_safety_deficit = round(safety_deficit, 2)
            baseline_exposure = round(exposure, 2)

        return weekly_breakdown

    base_weekly = run_projection(is_simulated=False)
    sim_weekly = run_projection(is_simulated=True)

    missing_unit_cost_count = len(missing_cost_skus)
    sim_id = f"SIM-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

    exposure_label = f"Financial Exposure: ${simulated_exposure:,.2f} (Partial calculation: {missing_unit_cost_count} SKUs excluded due to missing/zero/negative unit costs)."

    summary_notes = (
        f"Simulation '{run_name}': Demand multiplier {demand_multiplier}x, "
        f"Supplier capacity multiplier {supplier_capacity_multiplier}x, "
        f"Lead-time delay +{lead_time_delay_days} days. "
        f"Simulated Shortages: {simulated_shortages_count} (Baseline: {baseline_shortages_count}, Delta: {simulated_shortages_count - baseline_shortages_count:+d}). "
        f"{exposure_label}"
    )

    weekly_comparison_data = {
        "baseline_weekly": base_weekly,
        "simulated_weekly": sim_weekly,
        "weeks": weeks
    }

    run = SimulationRun(
        simulation_id=sim_id,
        run_name=run_name,
        demand_multiplier=demand_multiplier,
        supplier_capacity_multiplier=supplier_capacity_multiplier,
        lead_time_delay_days=lead_time_delay_days,
        baseline_shortages_count=baseline_shortages_count,
        simulated_shortages_count=simulated_shortages_count,
        baseline_total_shortage_qty=baseline_total_shortage_qty,
        simulated_total_shortage_qty=simulated_total_shortage_qty,
        baseline_backorder_qty=baseline_backorder_qty,
        simulated_backorder_qty=simulated_backorder_qty,
        baseline_safety_deficit=baseline_safety_deficit,
        simulated_safety_deficit=simulated_safety_deficit,
        baseline_exposure_value=baseline_exposure,
        simulated_exposure_value=simulated_exposure,
        affected_skus_count=len(affected_skus),
        affected_locations_count=len(affected_locs),
        missing_unit_cost_count=missing_unit_cost_count,
        created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        summary_notes=summary_notes,
        weekly_comparison_json=json.dumps(weekly_comparison_data)
    )

    try:
        db.add(run)
        db.commit()
        db.refresh(run)
    except Exception as e:
        db.rollback()
        raise e

    return run
