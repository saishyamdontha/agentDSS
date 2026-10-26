"""
AgentDSS — Impact Preview Engine (baseline-relative)
Impact(d) = w_c*dcost + w_t*dleadtime + w_r*drisk
dx = (x(d) - x0) / (x_hi - x_lo), with x and x0 clipped to [x_lo, x_hi] first.
x0 = value in the scenario's baseline state. Range [-1, 1]; lower is better.
Bounds and weights are fixed and reported; they must not change between runs.
"""

COST_LO, COST_HI = 4385.191, 30350980.0   # Fuel_Price_Index * Distance_km * Weight_MT (min/max)
LT_LO, LT_HI = 0.5, 80.8115               # Lead_Time_Days, upper bound = 95th percentile (clipped)
RISK_LO, RISK_HI = 0.0, 10.0              # Geopolitical_Risk_Score

W_COST, W_LEADTIME, W_RISK = 0.33, 0.33, 0.34


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _delta(value: float, base: float, lo: float, hi: float) -> float:
    return (_clip(value, lo, hi) - _clip(base, lo, hi)) / (hi - lo)


def _cost(row: dict) -> float:
    return row["Fuel_Price_Index"] * row["Distance_km"] * row["Weight_MT"]


def compute_preview(row: dict, baseline_row: dict) -> dict:
    d_cost = _delta(_cost(row), _cost(baseline_row), COST_LO, COST_HI)
    d_lt = _delta(row["Lead_Time_Days"], baseline_row["Lead_Time_Days"], LT_LO, LT_HI)
    d_risk = _delta(row["Geopolitical_Risk_Score"], baseline_row["Geopolitical_Risk_Score"], RISK_LO, RISK_HI)
    score = W_COST * d_cost + W_LEADTIME * d_lt + W_RISK * d_risk
    return {
        "impact_score": round(score, 4),
        "delta_cost": round(d_cost, 4),
        "delta_leadtime": round(d_lt, 4),
        "delta_risk": round(d_risk, 4),
        "weights": {"w_cost": W_COST, "w_leadtime": W_LEADTIME, "w_risk": W_RISK},
    }


if __name__ == "__main__":
    a = {"Fuel_Price_Index": 2.84, "Distance_km": 7750.0, "Weight_MT": 243.5,
         "Lead_Time_Days": 8.2, "Geopolitical_Risk_Score": 5.1}
    b = {"Fuel_Price_Index": 3.10, "Distance_km": 4000.0, "Weight_MT": 120.0,
         "Lead_Time_Days": 150.0, "Geopolitical_Risk_Score": 9.8}
    assert compute_preview(a, a)["impact_score"] == 0
    assert abs(compute_preview(a, b)["impact_score"] + compute_preview(b, a)["impact_score"]) < 1e-3
    print("candidate b vs baseline a:", compute_preview(b, a))
