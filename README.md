# SupplyChain IQ — Intelligent Demand & Inventory Optimization System

SupplyChain IQ is a full-stack supply-chain decision-support application built for deterministic multi-SKU, multi-location inventory projection, shortage detection, supplier capacity and lead-time validation, unit-of-measure (UOM) normalization, rule-based mitigation recommendations, and what-if scenario simulation.

The system transforms operational supply-chain data into explainable decisions with rigorous data-quality evaluation and confusion-matrix performance tracking.

> **Note:** SupplyChain IQ uses deterministic business rules, constraint engines, and synthetic or supplied operational data. It is not an ML-trained demand forecasting model.

---

## Key Features

- **Inventory Planning:** Sequential, SKU-location inventory projections across planning periods incorporating opening availability, inbound purchase orders, and production schedules.
- **Shortage Detection & Prioritization:** Identifies projected stock shortages and safety-stock violations, ranking them by severity, SKU criticality, and shortage quantity.
- **Supplier & Capacity Validation:** Evaluates supplier eligibility, SKU compatibility, lead times, minimum order quantities (MOQ), and weekly capacity limits.
- **Automated Mitigations:** Generates supplier purchase-order, approved-substitute, and production-increase options with approval workflows and audit logging.
- **Unit-of-Measure (UOM) Safety:** Enforces strict compatibility and conversion validation (e.g., KG to TON, BOX to PCS) with safe exclusion of unvalidated or incompatible quantities and idempotent issue logging.
- **What-If Scenario Simulation:** Evaluates demand surges, capacity reductions, and lead-time delays independently without mutating baseline operational inventory records.
- **Evaluation Engine:** Computes empirical confusion matrix metrics (True Positives, False Positives, True Negatives, False Negatives, Precision, Recall, F1-Score, and Accuracy) using strict 4-dimension `DetectorExecution` tracking.
- **Auditability:** Maintains decision explanations and operational logs for traceability.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Data Visualization** | Recharts |
| **Backend** | Python, FastAPI, SQLAlchemy, Custom Idempotent SQLite Migrations |
| **Database** | SQLite |
| **Data Processing** | Pandas, NumPy |
| **Testing & Build** | Pytest, TypeScript (`tsc`), Vite build |

---

## System Architecture

```text
              React + TypeScript Frontend (Port 3001)
                         |
                         | REST API (Vite Proxy /api -> Port 8000)
                         v
                   FastAPI Backend (Port 8000)
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
   Inventory Engine  Shortage Engine  Mitigation Engine
   (UOM Normalizer)  (Prioritizer)    (Approval Guardrails)
          |              |              |
          +--------------+--------------+
                         |
                         v
                Scenario Simulation
                         |
                         v
               Evaluation Engine (Confusion Matrix & 4-Dim Tracking)
                         |
                         v
                SQLite Database (Custom Startup Migrations)
```

---

## Core Business Workflow

1. Initialize master and transactional data via synthetic data generator.
2. Calculate sequential inventory projections for each SKU and location.
3. Identify projected shortages and safety-stock violations.
4. Prioritize shortages using deterministic criticality and severity rules.
5. Evaluate supplier capacity, MOQ, compatibility, and lead-time constraints.
6. Generate feasible mitigation recommendations.
7. Approve or reject recommendations through controlled workflows with audit logging.
8. Run what-if simulations to compare operational stress scenarios.
9. Evaluate data quality, anomaly detection, inventory reconciliation, and mitigation compliance.

---

## Core Formulas

### 1. Opening Available Inventory
```text
Opening Available = max(0, On-Hand Inventory - Reserved Inventory)
```

### 2. Closing Inventory Projection
```text
Closing Inventory =
    Opening Available
    + Eligible Inbound Purchase Orders (normalized to canonical UOM)
    + Eligible Production Plans
    - Forecast Demand
```
*Note: The closing inventory of period $t$ serves as the opening available inventory of period $t+1$.*

---

## Synthetic Starter Dataset

The application includes a configurable synthetic data generator (`backend/app/services/data_generator.py`).

Default starter configuration:

| Entity / Dataset | Default Quantity |
|---|---:|
| SKUs | 100 |
| Locations | 10 |
| Forecast Horizon | 12 weeks |
| Suppliers | 30 |
| Purchase Orders | 300 |
| Forecast Demand Records | 12,000 |

- **Random Seed:** `20261022` (Isolated RNG for reproducible datasets).

---

## Project Structure

```text
SupplyChain-IQ/
│
├── backend/
│   ├── app/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── services/      # Core engines (inventory, shortage, mitigation, simulation, evaluation, uom)
│   │   ├── routes/        # FastAPI API routers
│   │   ├── database.py    # Database connection & custom idempotent migrations
│   │   └── main.py        # FastAPI app factory & lifespan
│   ├── tests/             # Pytest test suite (79 backend tests passed at release verification)
│   └── requirements.txt
│
├── frontend/
│   ├── src/               # React components, views, and state management
│   ├── package.json
│   └── vite.config.ts     # Vite server config (port 3001, proxy /api to port 8000)
│
├── data/
│   └── ground_truth/      # Evaluation ground truth datasets (.csv, .json)
│
├── scripts/
│   ├── init_app.py        # App initialization & synthetic data seeding script
│   └── generate_data.py   # Synthetic data generation runner
│
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── ARCHITECTURE.md
│   ├── VALIDATION_REPORT.md
│   ├── TEST_RESULTS.md
│   ├── EVALUATION_REPORT.md
│   └── SOURCE_MANIFEST.md
│
└── AI_USAGE.md            # Prompt history & development documentation
```

---

## Prerequisites

- **Python:** 3.11 or later (with `py` launcher on Windows)
- **Node.js:** 18 or later
- **npm**

---

## Quick Start Guide

### 1. Clone the Repository
```powershell
git clone https://github.com/jravikumar960/SupplyChain-IQ.git
cd SupplyChain-IQ
```

### 2. Backend Setup & Startup
```powershell
# Install Python dependencies
py -m pip install -r backend/requirements.txt

# Initialize synthetic database and run startup migrations
py scripts/init_app.py
```
*Note: `init_app.py` initializes the SQLite database and populates synthetic operational data. Review local database settings before running if preserving existing custom records.*
```powershell
# Start the FastAPI backend server
py -m uvicorn backend.app.main:app --reload --port 8000
```
- **API Base URL:** [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)

### 3. Frontend Setup & Startup
Open a second PowerShell terminal:
```powershell
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server
npm run dev
```
- **Application UI:** [http://localhost:3001](http://localhost:3001)

### 4. Running Backend Tests
From the project root:
```powershell
py -m pytest backend/tests -v
```

### 5. Building the Frontend for Production
```powershell
npm --prefix frontend run build
```

---

## Documentation & Reports

- [Data Dictionary](docs/DATA_DICTIONARY.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Validation Report](docs/VALIDATION_REPORT.md)
- [Test Results](docs/TEST_RESULTS.md)
- [Evaluation Report](docs/EVALUATION_REPORT.md)
- [Source Manifest](docs/SOURCE_MANIFEST.md)
- [AI Usage and Development History](AI_USAGE.md)

---

## Current Scope and Limitations

- Inventory projections and mitigation recommendations are deterministic and rule-based.
- The application does not train or run machine-learning demand forecasting models.
- Synthetic starter data is provided for out-of-the-box evaluation.
- Scenario runs persist simulation summaries; they do not construct immutable historical snapshots of all transactional source records.
- Production deployments require environment-specific database configuration, authentication/authorization hardening, and operational security reviews.

---

## Project Objective

SupplyChain IQ demonstrates an explainable, robust approach to supply-chain planning by connecting deterministic multi-SKU, multi-location inventory projections, shortage prioritization, supplier constraint validation, rule-based mitigations, scenario analysis, and evaluation metrics into a cohesive full-stack application.
