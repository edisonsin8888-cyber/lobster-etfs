"""Pure deterministic scoring rules shared by the gold research scripts."""

from copy import deepcopy


SCORE_ENGINE_COMPONENT_SPEC = (
    {
        "metric": "Average GLD-Equity Rolling Correlation",
        "field": "average_gld_equity_correlation",
        "score_label": "Correlation Score",
        "weight": 0.30,
        "display_thresholds": (
            {
                "id": "correlation_full_score_boundary",
                "operator": "<=",
                "threshold": 0.0,
                "description": "Average correlation at or below 0.00 gives the clamped full score",
            },
        ),
        "scenario_target_id": "correlation_full_score_boundary",
        "favorable_direction": "decrease",
    },
    {
        "metric": "GLD / SPY Rolling Volatility Ratio",
        "field": "gld_spy_volatility_ratio",
        "score_label": "Volatility Score",
        "weight": 0.25,
        "display_thresholds": (
            {
                "id": "volatility_full_score_boundary",
                "operator": "<=",
                "threshold": 1.0,
                "score": 100,
                "description": "Volatility ratio at or below 1.00 gives 100",
            },
            {
                "id": "volatility_floor_score_boundary",
                "operator": ">=",
                "threshold": 2.0,
                "score": 30,
                "description": "Volatility ratio at or above 2.00 gives 30",
            },
        ),
        "scenario_target_id": "volatility_full_score_boundary",
        "favorable_direction": "decrease",
    },
    {
        "metric": "GLD Stress Return Minus SPY Stress Return",
        "field": "stress_return_gap",
        "score_label": "Stress Performance Score",
        "weight": 0.25,
        "display_thresholds": (
            {
                "id": "stress_full_score_boundary",
                "operator": ">=",
                "threshold": 0.025,
                "description": "Stress return gap at or above 0.025 gives the clamped full score",
            },
            {
                "id": "stress_zero_score_boundary",
                "operator": "<=",
                "threshold": -0.025,
                "description": "Stress return gap at or below -0.025 gives the clamped zero score",
            },
        ),
        "scenario_target_id": "stress_full_score_boundary",
        "favorable_direction": "increase",
    },
    {
        "metric": "GLD % Risk Contribution",
        "field": "gld_risk_contribution",
        "score_label": "Risk Contribution Score",
        "weight": 0.20,
        "display_thresholds": (
            {"operator": "<=", "threshold": 0.25, "score": 90},
            {"operator": "<=", "threshold": 0.35, "score": 70},
            {"operator": "<=", "threshold": 0.45, "score": 50},
            {"operator": ">", "threshold": 0.45, "score": 30},
        ),
        "scenario_target_id": None,
        "favorable_direction": "decrease",
    },
)

SCORE_ENGINE_WEIGHTS = {
    component["score_label"]: component["weight"]
    for component in SCORE_ENGINE_COMPONENT_SPEC
}


def score_engine_metadata():
    """Return score labels, weights, and thresholds without shared mutation."""

    return deepcopy(SCORE_ENGINE_COMPONENT_SPEC)


def _component(field):
    return next(item for item in SCORE_ENGINE_COMPONENT_SPEC if item["field"] == field)


def _threshold(field, threshold_id):
    component = _component(field)
    return next(
        item["threshold"]
        for item in component["display_thresholds"]
        if item.get("id") == threshold_id
    )


def clamp(x, low=0, high=100):
    return max(low, min(high, x))


def score_correlation(avg_corr):
    return clamp(100 * (1 - avg_corr))


def score_volatility(gld_vol, spy_vol):
    return score_volatility_ratio(gld_vol / spy_vol)


def score_volatility_ratio(ratio):
    full_score_boundary = _threshold(
        "gld_spy_volatility_ratio", "volatility_full_score_boundary"
    )
    floor_score_boundary = _threshold(
        "gld_spy_volatility_ratio", "volatility_floor_score_boundary"
    )
    if ratio <= full_score_boundary:
        return 100
    if ratio >= floor_score_boundary:
        return 30
    return clamp(100 - (ratio - full_score_boundary) * 70)


def score_stress(gld_stress, spy_stress):
    return score_stress_gap(gld_stress - spy_stress)


def score_stress_gap(stress_gap):
    return clamp(50 + stress_gap * 2000)


def score_risk_contribution(gld_rc):
    thresholds = _component("gld_risk_contribution")["display_thresholds"]
    for rule in thresholds:
        if rule["operator"] == "<=" and gld_rc <= rule["threshold"]:
            return rule["score"]
        if rule["operator"] == ">" and gld_rc > rule["threshold"]:
            return rule["score"]
    raise RuntimeError("Risk-contribution score specification has no fallback")


def calculate_final_score(scores):
    return (
        scores["Correlation Score"] * SCORE_ENGINE_WEIGHTS["Correlation Score"]
        + scores["Volatility Score"] * SCORE_ENGINE_WEIGHTS["Volatility Score"]
        + scores["Stress Performance Score"]
        * SCORE_ENGINE_WEIGHTS["Stress Performance Score"]
        + scores["Risk Contribution Score"]
        * SCORE_ENGINE_WEIGHTS["Risk Contribution Score"]
    )


def history_score_correlation(avg_corr):
    return max(0, 100 * (1 - avg_corr))


def history_score_volatility(vol_ratio):
    return max(0, min(100, 100 - max(vol_ratio - 1, 0) * 70))


def history_score_stress(stress_gap):
    return max(0, min(100, 50 + stress_gap * 2000))


def calculate_history_component_scores(avg_corr, vol_ratio, stress_gap):
    return (
        history_score_correlation(avg_corr),
        history_score_volatility(vol_ratio),
        history_score_stress(stress_gap),
    )


def calculate_history_gold_score(corr_score, vol_score, stress_score):
    return corr_score * 0.35 + vol_score * 0.30 + stress_score * 0.35
