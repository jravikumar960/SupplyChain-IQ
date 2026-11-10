def calculate_priority_score(severity: str, criticality: str, shortage_quantity: float) -> float:
    severity_weights = {"Critical": 40.0, "High": 25.0, "Medium": 10.0, "Low": 5.0}
    criticality_weights = {"Critical": 40.0, "High": 25.0, "Medium": 15.0, "Low": 5.0}

    s_score = severity_weights.get(severity, 10.0)
    c_score = criticality_weights.get(criticality, 15.0)
    qty_score = min(20.0, shortage_quantity / 100.0)

    total_score = round(s_score + c_score + qty_score, 2)
    return total_score
