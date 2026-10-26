"""
AgentDSS — Agent 1: Supplier
Reads real candidate shipments from backbone_dataset.csv, proposes ranked
options with confidence scores. STUB scoring — no LLM call yet.

Confidence is a composite of Carrier_Reliability_Score (higher is better)
and Lead_Time_Days (lower is better, normalized against the dataset's own
range so it's on a comparable [0,1] scale). A high-reliability option with
an extreme lead time should NOT outrank a moderate option with a reasonable
lead time — single-field ranking was tested and found operationally wrong.
"""

import pandas as pd

DATASET_PATH = "data/backbone_dataset.csv"
LEADTIME_MIN, LEADTIME_MAX = 0.5, 80.8115  # p95 cap, same as impact_preview.py


def _load_dataset() -> pd.DataFrame:
    return pd.read_csv(DATASET_PATH)


def _composite_confidence(reliability: float, lead_time: float) -> float:
    """Higher reliability = higher confidence. Higher lead time = lower confidence.
    Simple average of the two normalized signals — a stub, not a tuned model."""
    leadtime_norm = (lead_time - LEADTIME_MIN) / (LEADTIME_MAX - LEADTIME_MIN)
    leadtime_norm = max(0.0, min(1.0, leadtime_norm))
    speed_score = 1.0 - leadtime_norm  # fast = high score
    return round((reliability + speed_score) / 2, 3)


def generate_options(problem_statement: str, prior_decisions: list, n_options: int = 3) -> list[dict]:
    """
    Returns options_presented: [{"text": str, "confidence": float, "row": dict}, ...]
    STUB: samples n_options real rows, ranks by composite confidence
    (reliability + speed). Real version replaces sampling with an actual
    Claude API call reasoning over the disruption description, and should
    also filter candidates by relevance to the disrupted port/route —
    not yet implemented, flagged as a known gap.
    """
    df = _load_dataset()
    sample = df.sample(n=min(n_options, len(df)), random_state=None).copy()
    sample["composite_confidence"] = sample.apply(
        lambda r: _composite_confidence(r["Carrier_Reliability_Score"], r["Lead_Time_Days"]), axis=1
    )
    sample = sample.sort_values("composite_confidence", ascending=False)

    options = []
    for _, row in sample.iterrows():
        text = (
            f"Route via {row['Origin_Port']} -> {row['Destination_Port']} "
            f"({row['Transport_Mode']}), lead time {row['Lead_Time_Days']:.1f} days, "
            f"carrier reliability {row['Carrier_Reliability_Score']:.2f}"
        )
        options.append({
            "text": text,
            "confidence": float(row["composite_confidence"]),
            "row": row.to_dict(),
        })
    return options


if __name__ == "__main__":
    opts = generate_options("Primary supplier reports port closure, 5-day minimum delay.", [])
    for o in opts:
        print(o["text"], "-> confidence:", o["confidence"])
