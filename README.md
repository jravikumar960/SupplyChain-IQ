# SupplyChain IQ — Intelligent Demand & Inventory Optimization System

SupplyChain IQ is a full-stack enterprise application built for demand forecasting, deterministic multi-echelon inventory projection, shortage detection, supplier capacity validation, and automated rule-based mitigation recommendations.

## Prerequisites
- Python 3.11+ (with `py` launcher on Windows)
- Node.js 18+ & npm

## Quick Start (PowerShell)

### 1. Backend Setup & Startup
```powershell
# Install Python dependencies
py -m pip install -r backend/requirements.txt

# Generate synthetic dataset and run optimization engine
py scripts/init_app.py

# Run backend FastAPI server (with automatic SQLite schema migration on startup)
py -m uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup & Startup
```powershell
cd frontend
npm install
npm run dev
```
Open [http://localhost:3001](http://localhost:3001) in your browser.

### 3. Running Automated Tests
```powershell
py -m pytest backend/tests -v
```

## Documentation & Reports
- [Data Dictionary](docs/DATA_DICTIONARY.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Validation Report](docs/VALIDATION_REPORT.md)
- [Test Results](docs/TEST_RESULTS.md)
- [Evaluation Report](docs/EVALUATION_REPORT.md)
- [Source Manifest](docs/SOURCE_MANIFEST.md)
- [AI Usage](AI_USAGE.md)
