# SupplyChain IQ — Validation Report

## Automated Validation & QA Audit Summary

- **Primary-Key Uniqueness**: PASSED (0 duplicate primary keys across all tables).
- **Foreign-Key Integrity**: PASSED (100% valid foreign-key relationships).
- **Duplicate Inbound Detection (Anomaly A)**: PASSED (`ISSUE-001` detected duplicate POs and filtered them from inventory calculations).
- **Unapproved Substitute Blocking (Anomaly B)**: PASSED (`ISSUE-002` blocked unapproved substitutes from automated approval).
- **Supplier Capacity Constraints (Anomaly C)**: PASSED (`ISSUE-003` detected capacity over-allocation).
- **Lead-Time Consistency (Anomaly D)**: PASSED (`ISSUE-004` flagged missing lead-time data).
- **Unit of Measure Compatibility (Anomaly E)**: PASSED (`ISSUE-005` flagged UOM mismatches).
- **Automated Test Suite**: 8/8 Pytest tests passed successfully.
- **Reproducibility**: Verified across multiple runs with fixed seed `20261022` (100% deterministic dataset generation).
