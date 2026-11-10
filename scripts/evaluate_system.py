import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.services.evaluation_engine import evaluate_system_performance

if __name__ == "__main__":
    db = SessionLocal()
    metrics = evaluate_system_performance(db)
    db.close()
    print("=== SUPPLYCHAIN IQ EVALUATION METRICS ===")
    print(json.dumps(metrics, indent=2))
