import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.data_generator import generate_synthetic_data

if __name__ == "__main__":
    print("Generating SupplyChain IQ synthetic dataset...")
    generate_synthetic_data()
    print("Done!")
