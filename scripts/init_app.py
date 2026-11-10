import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.services.data_generator import generate_synthetic_data
from backend.app.services.shortage_engine import detect_and_save_shortages
from backend.app.services.mitigation_engine import generate_mitigations_for_shortages

if __name__ == "__main__":
    print("Initializing SupplyChain IQ dataset with explicit reset and running engines...")
    generate_synthetic_data(reset=True)
    db = SessionLocal()
    sc = detect_and_save_shortages(db)
    mc = generate_mitigations_for_shortages(db)
    db.close()
    print(f"Initialization complete! Detected {sc} shortages and generated {mc} mitigation options.")
