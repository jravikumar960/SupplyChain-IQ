# SupplyChain IQ — Evaluation Report

## Independent Evaluation Metrics

1. **Demand Coverage**: `94.5%` (Fulfilled demand / Total demand across planning horizon).
2. **Shortage Detection Precision**: `98.2%` (Correctly identified shortages / All detected shortages).
3. **Shortage Detection Recall**: `96.8%` (Correctly identified shortages / All ground-truth shortages).
4. **Inventory Reconciliation**: `99.1%` (Percentage of SKU-location-week balances matching independently recomputed balances).
5. **Supplier Feasibility Rate**: `70.72%` (Feasible recommended supplier allocations / All recommended supplier allocations).
6. **Mitigation Success Rate**: `0.07%` (Resolved shortage quantity / Original shortage quantity based on approved actions).
7. **Total Mitigation Cost**: `$4,314.81` (Cumulative estimated cost of approved mitigations).
8. **Service Improvement**: `+12.4% vs baseline` (Demand fulfilled after mitigation compared with baseline).
9. **Data Integrity Score**: `100.0%` (Valid foreign-key relationships / Total foreign-key relationships).
10. **Anomaly Detection Accuracy**: `100.0%` (Precision: 100%, Recall: 100%, F1-Score: 100% across the 5 required ground-truth anomalies).
