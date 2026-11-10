import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.services.validation_engine import run_validation

if __name__ == "__main__":
    report = run_validation()
    print("=== SUPPLYCHAIN IQ VALIDATION REPORT ===")
    print(json.dumps(report, indent=2))
