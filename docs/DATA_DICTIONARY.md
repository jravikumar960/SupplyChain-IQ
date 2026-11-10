# SupplyChain IQ — Data Dictionary

This document defines the relational database entities, fields, data types, and business constraints for SupplyChain IQ.

## Entities

### 1. SKU (Master)
- `sku_id` (VARCHAR, PK): Unique SKU identifier (e.g., `SKU-000001`).
- `sku_name` (VARCHAR): Product name and category description.
- `category` (VARCHAR): Product category (Electronics, Raw Materials, Packaging, etc.).
- `unit_of_measure` (VARCHAR): Standard UOM (PCS, KG, LTR, BOX, PALLET).
- `unit_cost` (FLOAT): Standard unit cost in USD.
- `criticality` (VARCHAR): Business criticality rating (Critical, High, Medium, Low).
- `is_active` (BOOLEAN): Active status flag.

### 2. Location (Master)
- `location_id` (VARCHAR, PK): Unique facility identifier (e.g., `LOC-000001`).
- `location_name` (VARCHAR): Name and region of facility.
- `location_type` (VARCHAR): Warehouse, DistributionCenter, RetailStore, Plant.
- `region` (VARCHAR): Geographic region.
- `storage_capacity` (FLOAT): Maximum storage capacity units.

### 3. ForecastDemand
- `demand_id` (VARCHAR, PK): Unique demand record ID.
- `sku_id` (VARCHAR, FK): References `SKU`.
- `location_id` (VARCHAR, FK): References `Location`.
- `week_start` (VARCHAR): Planning week (e.g., `2026-W01`).
- `forecast_quantity` (FLOAT): Projected customer demand quantity.
- `actual_quantity` (FLOAT, Optional): Realized actual demand.

### 4. Inventory
- `inventory_id` (VARCHAR, PK): Unique inventory stock record ID.
- `sku_id` (VARCHAR, FK): References `SKU`.
- `location_id` (VARCHAR, FK): References `Location`.
- `on_hand_quantity` (FLOAT): Physical units in stock.
- `reserved_quantity` (FLOAT): Allocated units.
- `safety_stock` (FLOAT): Minimum required buffer stock.
- `updated_at` (DATETIME): Last update timestamp.

### 5. Supplier & SupplierCapacity
- `supplier_id` (VARCHAR, PK): Unique supplier ID.
- `weekly_capacity` (FLOAT): Maximum weekly production/shipping volume.
- `minimum_order_quantity` (FLOAT): MOQ constraint.

### 6. Shortage
- `shortage_id` (VARCHAR, PK): Unique shortage ID.
- `shortage_quantity` (FLOAT): Units below threshold.
- `severity` (VARCHAR): Critical, High, Medium, Low.
- `root_cause` (VARCHAR): Explainable shortage cause.
- `priority_score` (FLOAT): Normalized priority ranking.

### 7. DataIssue (Exception Center)
- `issue_id` (VARCHAR, PK): Anomaly identifier (`ISSUE-001` to `ISSUE-005`).
- `issue_type` (VARCHAR): Injected anomaly type.
- `explanation` (TEXT): Detailed root cause and detection logic.
