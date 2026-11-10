from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base

class SKU(Base):
    __tablename__ = "skus"
    sku_id = Column(String, primary_key=True, index=True)
    sku_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit_of_measure = Column(String, nullable=False)
    unit_cost = Column(Float, nullable=True) # Allow null for missing cost tests
    criticality = Column(String, nullable=False) # Critical, High, Medium, Low
    is_active = Column(Boolean, default=True)

    demands = relationship("ForecastDemand", back_populates="sku")
    inventories = relationship("Inventory", back_populates="sku")
    supplier_capacities = relationship("SupplierCapacity", back_populates="sku")
    lead_times = relationship("LeadTime", back_populates="sku")
    purchase_orders = relationship("PurchaseOrder", back_populates="sku")
    production_plans = relationship("ProductionPlan", back_populates="sku")
    shortages = relationship("Shortage", back_populates="sku")
    bom_parents = relationship("BOM", foreign_keys="[BOM.parent_sku_id]", back_populates="parent_sku")
    bom_components = relationship("BOM", foreign_keys="[BOM.component_sku_id]", back_populates="component_sku")
    substitutes = relationship("SKUSubstitute", foreign_keys="[SKUSubstitute.sku_id]", back_populates="sku")

class Location(Base):
    __tablename__ = "locations"
    location_id = Column(String, primary_key=True, index=True)
    location_name = Column(String, nullable=False)
    location_type = Column(String, nullable=False) # Warehouse, DistributionCenter, RetailStore, Plant
    region = Column(String, nullable=False)
    storage_capacity = Column(Float, nullable=False)

    demands = relationship("ForecastDemand", back_populates="location")
    inventories = relationship("Inventory", back_populates="location")
    purchase_orders = relationship("PurchaseOrder", back_populates="location")
    production_plans = relationship("ProductionPlan", back_populates="location")
    shortages = relationship("Shortage", back_populates="location")

class ForecastDemand(Base):
    __tablename__ = "forecast_demands"
    demand_id = Column(String, primary_key=True, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False, index=True)
    week_start = Column(String, nullable=False, index=True) # e.g. "2026-W01"
    forecast_quantity = Column(Float, nullable=False)
    actual_quantity = Column(Float, nullable=True)

    sku = relationship("SKU", back_populates="demands")
    location = relationship("Location", back_populates="demands")

class Inventory(Base):
    __tablename__ = "inventories"
    inventory_id = Column(String, primary_key=True, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False, index=True)
    on_hand_quantity = Column(Float, nullable=False)
    reserved_quantity = Column(Float, nullable=False)
    safety_stock = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    sku = relationship("SKU", back_populates="inventories")
    location = relationship("Location", back_populates="inventories")

class Supplier(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(String, primary_key=True, index=True)
    supplier_name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    reliability_score = Column(Float, nullable=False) # 0.0 to 1.0
    is_active = Column(Boolean, default=True)

    capacities = relationship("SupplierCapacity", back_populates="supplier")
    lead_times = relationship("LeadTime", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class SupplierCapacity(Base):
    __tablename__ = "supplier_capacities"
    capacity_id = Column(String, primary_key=True, index=True)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    weekly_capacity = Column(Float, nullable=False)
    minimum_order_quantity = Column(Float, nullable=False)
    effective_from = Column(String, nullable=False)
    effective_to = Column(String, nullable=False)

    supplier = relationship("Supplier", back_populates="capacities")
    sku = relationship("SKU", back_populates="supplier_capacities")

class LeadTime(Base):
    __tablename__ = "lead_times"
    lead_time_id = Column(String, primary_key=True, index=True)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=True, index=True) # Can be missing for exception D
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    min_days = Column(Integer, nullable=False)
    average_days = Column(Integer, nullable=False)
    max_days = Column(Integer, nullable=False)

    supplier = relationship("Supplier", back_populates="lead_times")
    sku = relationship("SKU", back_populates="lead_times")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    po_id = Column(String, primary_key=True, index=True)
    supplier_id = Column(String, ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False, index=True)
    ordered_quantity = Column(Float, nullable=False)
    received_quantity = Column(Float, nullable=False)
    expected_delivery_date = Column(String, nullable=False)
    status = Column(String, nullable=False, index=True) # Pending, Received, Delayed, Cancelled
    is_duplicate = Column(Boolean, default=False, index=True) # For anomaly A

    supplier = relationship("Supplier", back_populates="purchase_orders")
    sku = relationship("SKU", back_populates="purchase_orders")
    location = relationship("Location", back_populates="purchase_orders")

class ProductionPlan(Base):
    __tablename__ = "production_plans"
    production_id = Column(String, primary_key=True, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False, index=True)
    planned_quantity = Column(Float, nullable=False)
    production_start = Column(String, nullable=False)
    production_end = Column(String, nullable=False)
    capacity_available = Column(Float, nullable=False)
    status = Column(String, nullable=False, index=True) # Planned, InProgress, Completed, Cancelled

    sku = relationship("SKU", back_populates="production_plans")
    location = relationship("Location", back_populates="production_plans")

class Shortage(Base):
    __tablename__ = "shortages"
    shortage_id = Column(String, primary_key=True, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False, index=True)
    week_start = Column(String, nullable=False, index=True)
    demand_quantity = Column(Float, nullable=False)
    projected_available = Column(Float, nullable=False)
    shortage_quantity = Column(Float, nullable=False)
    severity = Column(String, nullable=False, index=True) # Critical, High, Medium, Low
    root_cause = Column(String, nullable=False)
    priority_score = Column(Float, nullable=False)
    status = Column(String, nullable=False, index=True) # Open, Mitigated, Ignored

    sku = relationship("SKU", back_populates="shortages")
    location = relationship("Location", back_populates="shortages")
    mitigations = relationship("MitigationOption", back_populates="shortage")

class MitigationOption(Base):
    __tablename__ = "mitigation_options"
    mitigation_id = Column(String, primary_key=True, index=True)
    shortage_id = Column(String, ForeignKey("shortages.shortage_id"), nullable=False, index=True)
    mitigation_type = Column(String, nullable=False) # SupplierPO, AlternativeSupplier, SubstituteSKU, ProductionIncrease, InventoryTransfer
    proposed_quantity = Column(Float, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    expected_arrival_date = Column(String, nullable=False)
    service_impact = Column(String, nullable=False) # High, Medium, Low
    feasibility_status = Column(String, nullable=False, index=True) # Feasible, Infeasible, Unknown
    feasibility_explanation = Column(Text, nullable=True)
    supplier_id = Column(String, nullable=True)
    recommendation_score = Column(Float, nullable=False)
    is_approved = Column(Boolean, default=False, index=True)

    shortage = relationship("Shortage", back_populates="mitigations")
    decision = relationship("MitigationDecision", back_populates="mitigation", uselist=False)

class BOM(Base):
    __tablename__ = "boms"
    bom_id = Column(String, primary_key=True, index=True)
    parent_sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    component_sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    quantity_required = Column(Float, nullable=False)

    parent_sku = relationship("SKU", foreign_keys=[parent_sku_id], back_populates="bom_parents")
    component_sku = relationship("SKU", foreign_keys=[component_sku_id], back_populates="bom_components")

class SKUSubstitute(Base):
    __tablename__ = "sku_substitutes"
    substitute_id = Column(String, primary_key=True, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    substitute_sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    is_approved = Column(Boolean, nullable=False)
    compatibility_notes = Column(Text, nullable=False)

    sku = relationship("SKU", foreign_keys=[sku_id], back_populates="substitutes")

class InventoryEvent(Base):
    __tablename__ = "inventory_events"
    event_id = Column(String, primary_key=True, index=True)
    sku_id = Column(String, ForeignKey("skus.sku_id"), nullable=False)
    location_id = Column(String, ForeignKey("locations.location_id"), nullable=False)
    change_quantity = Column(Float, nullable=False)
    event_type = Column(String, nullable=False)
    reference_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    explanation = Column(Text, nullable=False)

class PurchaseOrderEvent(Base):
    __tablename__ = "purchase_order_events"
    event_id = Column(String, primary_key=True, index=True)
    po_id = Column(String, ForeignKey("purchase_orders.po_id"), nullable=False)
    previous_status = Column(String, nullable=False)
    new_status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    explanation = Column(Text, nullable=False)

class MitigationDecision(Base):
    __tablename__ = "mitigation_decisions"
    decision_id = Column(String, primary_key=True, index=True)
    mitigation_id = Column(String, ForeignKey("mitigation_options.mitigation_id"), nullable=False)
    decision_status = Column(String, nullable=False) # Approved, Rejected
    decided_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    user_notes = Column(Text, nullable=True)

    mitigation = relationship("MitigationOption", back_populates="decision")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_id = Column(String, primary_key=True, index=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=False)
    event_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    explanation = Column(Text, nullable=False)

class DataIssue(Base):
    __tablename__ = "data_issues"
    issue_id = Column(String, primary_key=True, index=True)
    issue_type = Column(String, nullable=False) # INBOUND_COUNTED_TWICE, SUBSTITUTE_NOT_APPROVED, SUPPLIER_CAPACITY_EXCEEDED, SHORTAGE_WITHOUT_LEAD_TIME, UNIT_OF_MEASURE_MISMATCH
    affected_entity_type = Column(String, nullable=False)
    affected_entity_id = Column(String, nullable=False)
    detection_result = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    resolution_status = Column(String, nullable=False) # Detected, Flagged, Resolved

class SimulationRun(Base):
    __tablename__ = "simulation_runs"
    simulation_id = Column(String, primary_key=True, index=True)
    run_name = Column(String, nullable=False)
    demand_multiplier = Column(Float, nullable=False)
    supplier_capacity_multiplier = Column(Float, nullable=False)
    lead_time_delay_days = Column(Integer, nullable=False)
    baseline_shortages_count = Column(Integer, nullable=False)
    simulated_shortages_count = Column(Integer, nullable=False)
    baseline_total_shortage_qty = Column(Float, nullable=False, default=0.0)
    simulated_total_shortage_qty = Column(Float, nullable=False, default=0.0)
    baseline_backorder_qty = Column(Float, nullable=False, default=0.0)
    simulated_backorder_qty = Column(Float, nullable=False, default=0.0)
    baseline_safety_deficit = Column(Float, nullable=False, default=0.0)
    simulated_safety_deficit = Column(Float, nullable=False, default=0.0)
    baseline_exposure_value = Column(Float, nullable=False)
    simulated_exposure_value = Column(Float, nullable=False)
    affected_skus_count = Column(Integer, nullable=False, default=0)
    affected_locations_count = Column(Integer, nullable=False, default=0)
    missing_unit_cost_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    summary_notes = Column(Text, nullable=True)
    weekly_comparison_json = Column(Text, nullable=True)
