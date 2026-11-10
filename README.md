# SupplyChain IQ — Intelligent Demand & Inventory Optimization System

SupplyChain IQ is a full-stack enterprise application built for demand forecasting, inventory projection, shortage detection, supplier capacity validation, and automated mitigation recommendations.

## Quick Start (PowerShell)

### 1. Backend Setup & Startup
```powershell
# Install python dependencies
py -m pip install -r backend/requirements.txt

# Generate synthetic dataset and run engines
py scripts/init_app.py

# Run backend FastAPI server
py -m uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend Setup & Startup
```powershell
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Running Automated Tests
```powershell
py -m pytest backend/tests/test_supplychain.py -v
```

## Documentation & Reports
- [Data Dictionary](docs/DATA_DICTIONARY.md)
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Validation Report](docs/VALIDATION_REPORT.md)
- [Test Results](docs/TEST_RESULTS.md)
- [Evaluation Report](docs/EVALUATION_REPORT.md)
- [Source Manifest](docs/SOURCE_MANIFEST.md)
- [AI Usage](AI_USAGE.md)
