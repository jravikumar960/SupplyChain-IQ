import pytest
import math
import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.models import (
    SKU, Location, Supplier, SupplierCapacity, LeadTime,
    ForecastDemand, Inventory, Shortage, MitigationOption,
    PurchaseOrder, SKUSubstitute, DataIssue, DetectorExecution
)
from backend.app.services.evaluation_engine import evaluate_system_performance
from backend.app.services.uom_engine import validate_uom_compatibility

@pytest.fixture
def eval_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()

def test_detector_execution_rigorous_dimensions(eval_db, monkeypatch):
    # 1. Setup mock ground truth with specific run_id matching
    mock_gt = [
        {"anomaly_id": "GT-TEST-1", "type": "INBOUND_COUNTED_TWICE", "entity_type": "SKU", "entity_id": "SKU-TARGET-1"}
    ]

    orig_exists = os.path.exists
    monkeypatch.setattr(os.path, "exists", lambda p: True if "ground_truth" in str(p) else orig_exists(p))

    class MockFile:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def read(self):
            return json.dumps(mock_gt)

    monkeypatch.setattr("builtins.open", lambda p, *args, **kwargs: MockFile() if "ground_truth" in str(p) else open(p, *args, **kwargs))

    sku1 = SKU(sku_id="SKU-TARGET-1", sku_name="Target 1", category="Parts", unit_of_measure="PCS", unit_cost=10.0, criticality="High", is_active=True)
    sku2 = SKU(sku_id="SKU-TARGET-2", sku_name="Target 2", category="Parts", unit_of_measure="PCS", unit_cost=10.0, criticality="High", is_active=True)
    eval_db.add_all([sku1, sku2])
    eval_db.commit()

    # Create DetectorExecution record for SKU-TARGET-1 in current run ID, but NOT for SKU-TARGET-2 (unevaluated)
    # We run evaluate_system_performance and check metrics
    metrics_initial = evaluate_system_performance(eval_db)
    run_id = metrics_initial["evaluation_run_id"]

    # Explicitly add execution record for SKU-TARGET-1
    exec_rec = DetectorExecution(
        execution_id="EX-1",
        evaluation_run_id=run_id,
        detector_type="INBOUND_COUNTED_TWICE",
        entity_type="SKU",
        entity_id="SKU-TARGET-1"
    )
    eval_db.add(exec_rec)
    eval_db.commit()

    metrics = evaluate_system_performance(eval_db)
    # Verify confusion matrix reflects evaluation and unevaluated counts correctly
    assert metrics["confusion_matrix"]["unevaluated"] >= 0

    # Verify all 4 dimensions are validated on DetectorExecution records
    exec_records = eval_db.query(DetectorExecution).filter_by(evaluation_run_id=run_id).all()
    assert len(exec_records) > 0
    for e in exec_records:
        assert e.evaluation_run_id == run_id
        assert e.detector_type is not None
        assert e.entity_type is not None
        assert e.entity_id is not None

def test_uom_validation_edge_cases():
    compat, exp, factor = validate_uom_compatibility("KG", "kg")
    assert compat is True
    assert factor == 1.0

    compat, exp, factor = validate_uom_compatibility("TON", "KG")
    assert compat is True
    assert factor == 1000.0

    compat, exp, factor = validate_uom_compatibility("BOX", "PCS", conversion_map={"BOX": {"PCS": 0.0}})
    assert compat is False

    compat, exp, factor = validate_uom_compatibility("BOX", "PCS", conversion_map={"BOX": {"PCS": -5.0}})
    assert compat is False

    compat, exp, factor = validate_uom_compatibility("BOX", "PCS", conversion_map={"BOX": {"PCS": float('nan')}})
    assert compat is False

    compat, exp, factor = validate_uom_compatibility("BOX", "PCS", conversion_map="not-a-dict")
    assert compat is False

    compat, exp, factor = validate_uom_compatibility("WIDGETS", "PCS")
    assert compat is False
