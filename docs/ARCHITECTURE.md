# SupplyChain IQ — Architecture Documentation

## System Overview
SupplyChain IQ is a full-stack, intelligent demand and inventory optimization platform engineered for enterprise supply chain resilience.

## Architecture Layers
1. **Frontend**: React, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React.
2. **Backend API**: FastAPI (Python 3.10+), SQLAlchemy ORM, Pydantic validation schemas.
3. **Database**: SQLite (`data/supplychain_iq.db`) with zero external infrastructure setup.
4. **Deterministic Optimization Engines**:
   - Demand Calculation Engine
   - Inventory Projection Engine (Projected Available Balance formula with duplicate receipt filtering)
   - Shortage Detection & Root Cause Analysis Engine
   - Supplier & Production Feasibility Engine
   - Mitigation Option Evaluator & Prioritization Engine
   - Audit & Traceability Engine
   - Evaluation & Validation Engine (measuring coverage, precision, recall, data integrity, and detecting the 5 required anomalies)
