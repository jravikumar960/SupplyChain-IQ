import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.data_generator import generate_synthetic_data

if __name__ == "__main__":
    print("Generating SupplyChain IQ synthetic dataset (non-destructive/idempotent)...")
    generate_synthetic_data(reset=False)
    print("Done!")
