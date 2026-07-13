"""Pure, import-safe decision helpers for gold allocation guidance."""

from copy import deepcopy
import operator


_OPERATORS = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}


_ALLOCATION_HISTORY_SCORE_DEPENDENCY = {
    "type": "derived_allocation_history_score",
    "input_fields": (
        {
            "input_field": "average_gld_equity_correlation",
            "favorable_direction": "decrease",
        },
        {
            "input_field": "gld_spy_volatility_ratio",
            "favorable_direction": "decrease",
        },
        {
            "input_field": "stress_return_gap",
            "favorable_direction": "increase",
        },
    ),
    "description": (
        "Derived from allocation-history correlation, volatility-ratio, and "
        "stress-gap component scores"
    ),
}


GOLD_ALLOCATION_RULE_SPEC = {
    "range_order": ("0%–5%", "5%–10%", "5%–15%"),
    "allocation_score": {
        "base_score": 50,
        "minimum": 0,
        "maximum": 100,
        "groups": (
            {
                "mode": "independent",
                "rules": (
                    {
                        "id": "stress_gap_positive",
                        "field": "stress_gap",
                        "operator": ">",
                        "threshold": 0.0,
                        "points": 15,
                        "description": "Stress-period return gap is positive",
                    },
                ),
            },
            {
                "mode": "first_match",
                "rules": (
                    {
                        "id": "average_correlation_below_0_45",
                        "field": "avg_corr",
                        "operator": "<",
                        "threshold": 0.45,
                        "points": 10,
                        "description": "Average GLD-equity correlation is below 0.45",
                    },
                    {
                        "id": "average_correlation_above_0_65",
                        "field": "avg_corr",
                        "operator": ">",
                        "threshold": 0.65,
                        "points": -10,
                        "description": "Average GLD-equity correlation is above 0.65",
                    },
                ),
            },
            {
                "mode": "first_match",
                "rules": (
                    {
                        "id": "volatility_ratio_below_1_50",
                        "field": "vol_ratio",
                        "operator": "<",
                        "threshold": 1.50,
                        "points": 10,
                        "description": "GLD/SPY volatility ratio is below 1.50",
                    },
                    {
                        "id": "volatility_ratio_above_1_80",
                        "field": "vol_ratio",
                        "operator": ">",
                        "threshold": 1.80,
                        "points": -10,
                        "description": "GLD/SPY volatility ratio is above 1.80",
                    },
                ),
            },
            {
                "mode": "first_match",
                "rules": (
                    {
                        "id": "score_at_least_60",
                        "field": "score",
                        "operator": ">=",
                        "threshold": 60.0,
                        "points": 10,
                        "description": "Historical three-component score is at least 60",
                    },
                    {
                        "id": "score_below_45",
                        "field": "score",
                        "operator": "<",
                        "threshold": 45.0,
                        "points": -10,
                        "description": "Historical three-component score is below 45",
                    },
                ),
            },
        ),
    },
    "strategic_ranges": (
        {
            "id": "supports_5_to_15",
            "range": "5%–15%",
            "description": "All conditions required for the 5%–15% strategic range",
            "predicates": (
                {
                    "id": "stress_gap_positive",
                    "field": "stress_gap",
                    "dependency": {
                        "type": "input",
                        "input_field": "stress_return_gap",
                    },
                    "operator": ">",
                    "threshold": 0.0,
                    "target_range": "5%–15%",
                    "description": "Stress-period return gap is positive",
                },
                {
                    "id": "score_at_least_55",
                    "field": "score",
                    "dependency": _ALLOCATION_HISTORY_SCORE_DEPENDENCY,
                    "operator": ">=",
                    "threshold": 55.0,
                    "target_range": "5%–15%",
                    "description": "Historical three-component score is at least 55",
                },
                {
                    "id": "average_correlation_below_0_60",
                    "field": "avg_corr",
                    "dependency": {
                        "type": "input",
                        "input_field": "average_gld_equity_correlation",
                    },
                    "operator": "<",
                    "threshold": 0.60,
                    "target_range": "5%–15%",
                    "description": "Average GLD-equity correlation is below 0.60",
                },
                {
                    "id": "volatility_ratio_below_1_80",
                    "field": "vol_ratio",
                    "dependency": {
                        "type": "input",
                        "input_field": "gld_spy_volatility_ratio",
                    },
                    "operator": "<",
                    "threshold": 1.80,
                    "target_range": "5%–15%",
                    "description": "GLD/SPY volatility ratio is below 1.80",
                },
            ),
        },
        {
            "id": "supports_5_to_10",
            "range": "5%–10%",
            "description": "All conditions required for the 5%–10% strategic range",
            "predicates": (
                {
                    "id": "stress_gap_positive",
                    "field": "stress_gap",
                    "dependency": {
                        "type": "input",
                        "input_field": "stress_return_gap",
                    },
                    "operator": ">",
                    "threshold": 0.0,
                    "target_range": "5%–10%",
                    "description": "Stress-period return gap is positive",
                },
                {
                    "id": "score_at_least_45",
                    "field": "score",
                    "dependency": _ALLOCATION_HISTORY_SCORE_DEPENDENCY,
                    "operator": ">=",
                    "threshold": 45.0,
                    "target_range": "5%–10%",
                    "description": "Historical three-component score is at least 45",
                },
                {
                    "id": "average_correlation_below_0_70",
                    "field": "avg_corr",
                    "dependency": {
                        "type": "input",
                        "input_field": "average_gld_equity_correlation",
                    },
                    "operator": "<",
                    "threshold": 0.70,
                    "target_range": "5%–10%",
                    "description": "Average GLD-equity correlation is below 0.70",
                },
            ),
        },
        {
            "id": "fallback_0_to_5",
            "range": "0%–5%",
            "description": "Fallback when no higher strategic range is supported",
            "predicates": (),
        },
    ),
    "alerts": {
        "red": {
            "minimum_matches": 2,
            "predicates": (
                {
                    "id": "average_correlation_at_least_0_60",
                    "field": "avg_corr",
                    "operator": ">=",
                    "threshold": 0.60,
                    "description": "Average GLD-equity correlation is at least 0.60",
                },
                {
                    "id": "volatility_ratio_at_least_1_70",
                    "field": "vol_ratio",
                    "operator": ">=",
                    "threshold": 1.70,
                    "description": "GLD/SPY volatility ratio is at least 1.70",
                },
                {
                    "id": "score_below_45",
                    "field": "score",
                    "operator": "<",
                    "threshold": 45.0,
                    "description": "Historical three-component score is below 45",
                },
            ),
        },
        "yellow": {
            "minimum_matches": 2,
            "predicates": (
                {
                    "id": "average_correlation_at_least_0_30",
                    "field": "avg_corr",
                    "operator": ">=",
                    "threshold": 0.30,
                    "description": "Average GLD-equity correlation is at least 0.30",
                },
                {
                    "id": "volatility_ratio_at_least_1_20",
                    "field": "vol_ratio",
                    "operator": ">=",
                    "threshold": 1.20,
                    "description": "GLD/SPY volatility ratio is at least 1.20",
                },
                {
                    "id": "score_below_70",
                    "field": "score",
                    "operator": "<",
                    "threshold": 70.0,
                    "description": "Historical three-component score is below 70",
                },
            ),
        },
    },
    "best_step": (
        {
            "result": "0% to 5%",
            "mode": "any",
            "predicates": (
                {
                    "id": "score_below_45",
                    "field": "score",
                    "operator": "<",
                    "threshold": 45.0,
                    "description": "Historical three-component score is below 45",
                },
                {
                    "id": "volatility_ratio_above_2_00",
                    "field": "vol_ratio",
                    "operator": ">",
                    "threshold": 2.00,
                    "description": "GLD/SPY volatility ratio is above 2.00",
                },
            ),
        },
        {
            "result": "5% to 10%",
            "mode": "all",
            "predicates": (
                {
                    "id": "stress_gap_positive",
                    "field": "stress_gap",
                    "operator": ">",
                    "threshold": 0.0,
                    "description": "Stress-period return gap is positive",
                },
                {
                    "id": "score_at_least_55",
                    "field": "score",
                    "operator": ">=",
                    "threshold": 55.0,
                    "description": "Historical three-component score is at least 55",
                },
            ),
        },
        {
            "result": "0% to 5%",
            "mode": "fallback",
            "predicates": (),
        },
    ),
    "confidence": (
        {"operator": ">=", "threshold": 70.0, "result": "High"},
        {"operator": ">=", "threshold": 55.0, "result": "Medium"},
        {"operator": None, "threshold": None, "result": "Low"},
    ),
    "allocation_stance": (
        {"operator": ">=", "threshold": 70.0, "result": "Supportive"},
        {"operator": ">=", "threshold": 55.0, "result": "Cautious"},
        {"operator": None, "threshold": None, "result": "Defensive"},
    ),
}


def _values(score, stress_gap, avg_corr, vol_ratio):
    return {
        "score": score,
        "stress_gap": stress_gap,
        "avg_corr": avg_corr,
        "vol_ratio": vol_ratio,
    }


def _matches(predicate, values):
    return _OPERATORS[predicate["operator"]](
        values[predicate["field"]], predicate["threshold"]
    )


def allocation_rule_metadata():
    """Return scenario-ready authoritative rule metadata without shared mutation."""

    return deepcopy(GOLD_ALLOCATION_RULE_SPEC)


def score_status(score):
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Moderate"
    if score >= 40:
        return "Mixed"
    return "Weak"


def confidence(score):
    for rule in GOLD_ALLOCATION_RULE_SPEC["confidence"]:
        if rule["operator"] is None or _OPERATORS[rule["operator"]](
            score, rule["threshold"]
        ):
            return rule["result"]
    raise RuntimeError("Confidence rule specification has no fallback")


def alert_level(avg_corr, vol_ratio, score):
    values = _values(score, 0.0, avg_corr, vol_ratio)
    alerts = GOLD_ALLOCATION_RULE_SPEC["alerts"]
    red_count = sum(_matches(item, values) for item in alerts["red"]["predicates"])
    yellow_count = sum(
        _matches(item, values) for item in alerts["yellow"]["predicates"]
    )

    if red_count >= alerts["red"]["minimum_matches"]:
        return "Red"
    if red_count == 1 or yellow_count >= alerts["yellow"]["minimum_matches"]:
        return "Yellow"
    return "Green"


def allocation_score(score, stress_gap, avg_corr, vol_ratio):
    spec = GOLD_ALLOCATION_RULE_SPEC["allocation_score"]
    values = _values(score, stress_gap, avg_corr, vol_ratio)
    result = spec["base_score"]

    for group in spec["groups"]:
        for rule in group["rules"]:
            if _matches(rule, values):
                result += rule["points"]
                if group["mode"] == "first_match":
                    break

    return max(spec["minimum"], min(spec["maximum"], result))


def strategic_range(score, avg_corr, vol_ratio, stress_gap):
    values = _values(score, stress_gap, avg_corr, vol_ratio)
    for rule in GOLD_ALLOCATION_RULE_SPEC["strategic_ranges"]:
        if all(_matches(item, values) for item in rule["predicates"]):
            return rule["range"]
    raise RuntimeError("Strategic-range rule specification has no fallback")


def best_step(score, stress_gap, vol_ratio):
    values = _values(score, stress_gap, 0.0, vol_ratio)
    for rule in GOLD_ALLOCATION_RULE_SPEC["best_step"]:
        matches = [_matches(item, values) for item in rule["predicates"]]
        if rule["mode"] == "fallback":
            return rule["result"]
        if rule["mode"] == "any" and any(matches):
            return rule["result"]
        if rule["mode"] == "all" and all(matches):
            return rule["result"]
    raise RuntimeError("Best-step rule specification has no fallback")


def direction(change, threshold=2):
    if change > threshold:
        return "Improving"
    if change < -threshold:
        return "Deteriorating"
    return "Stable"


def range_transition(prev, curr):
    order = {
        value: index
        for index, value in enumerate(GOLD_ALLOCATION_RULE_SPEC["range_order"])
    }
    diff = order[curr] - order[prev]

    if diff > 0:
        return "Loosened"
    if diff < 0:
        return "Tightened"
    return "Unchanged"


def alert_transition(prev, curr):
    order = {"Green": 0, "Yellow": 1, "Red": 2}
    diff = order[curr] - order[prev]

    if diff > 0:
        return "Deteriorated"
    if diff < 0:
        return "Improved"
    return "Unchanged"


def allocation_stance(allocation_score):
    for rule in GOLD_ALLOCATION_RULE_SPEC["allocation_stance"]:
        if rule["operator"] is None or _OPERATORS[rule["operator"]](
            allocation_score, rule["threshold"]
        ):
            return rule["result"]
    raise RuntimeError("Allocation-stance rule specification has no fallback")


def allocation_rule_trace(score, stress_gap, avg_corr, vol_ratio):
    """Return production decisions and predicates from one authoritative spec."""

    values = _values(score, stress_gap, avg_corr, vol_ratio)
    alerts = GOLD_ALLOCATION_RULE_SPEC["alerts"]
    range_rules = GOLD_ALLOCATION_RULE_SPEC["strategic_ranges"]
    score_groups = GOLD_ALLOCATION_RULE_SPEC["allocation_score"]["groups"]

    adjustments = {}
    for group in score_groups:
        for rule in group["rules"]:
            adjustments[rule["id"]] = rule["points"] if _matches(rule, values) else 0

    alloc_score = allocation_score(score, stress_gap, avg_corr, vol_ratio)
    return {
        "alert_level": alert_level(avg_corr, vol_ratio, score),
        "alert_conditions": {
            level: {
                rule["id"]: _matches(rule, values)
                for rule in alerts[level]["predicates"]
            }
            for level in ("red", "yellow")
        },
        "allocation_guidance_score": alloc_score,
        "allocation_adjustments": adjustments,
        "recommended_strategic_range": strategic_range(
            score, avg_corr, vol_ratio, stress_gap
        ),
        "range_conditions": {
            rule["id"]: {
                predicate["id"]: _matches(predicate, values)
                for predicate in rule["predicates"]
            }
            for rule in range_rules
            if rule["predicates"]
        },
        "best_marginal_step": best_step(score, stress_gap, vol_ratio),
        "recommendation_confidence": confidence(alloc_score),
        "allocation_stance": allocation_stance(alloc_score),
    }
