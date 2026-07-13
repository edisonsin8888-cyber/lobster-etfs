"""Create deterministic, non-predictive GLD decision-boundary evidence."""

from __future__ import annotations

import json
from itertools import combinations, product
import math
from pathlib import Path
import sys
from typing import Any

import pandas as pd

from gold_decision_rules import (
    calculate_final_score,
    calculate_history_component_scores,
    calculate_history_gold_score,
    score_correlation,
    score_engine_metadata,
    score_risk_contribution,
    score_stress_gap,
    score_volatility_ratio,
)
from gold_utils import allocation_rule_metadata, allocation_rule_trace, score_status


SCHEMA_VERSION = "1.0.0"
CORE_TICKERS = {"SPY", "QQQ", "GLD", "TLT"}
SCORE_FILE = Path("reports/06_score_and_monitor/gold_diversification_score.csv")
HISTORY_FILE = Path("reports/06_score_and_monitor/allocation_history.csv")
QUALITY_FILE = Path("reports/08_agent_ops/data_quality_report.csv")
OUTPUT_FILE = Path("reports/07_ai_research/decision_boundary_explorer.json")

QUALITY_COLUMNS = [
    "Ticker", "Status", "Rows", "Missing Close Values", "Duplicate Dates",
    "Latest Date", "Days Since Latest", "Abnormal Return Count", "Issues",
]
SCORE_COLUMNS = ["Metric", "Value", "Score"]
HISTORY_COLUMNS = [
    "Date", "Gold Diversification Score", "Status", "Alert Level",
    "Allocation Guidance Score", "Recommendation Confidence", "Best Marginal Step",
    "Recommended Strategic Range", "Average GLD-Equity Correlation",
    "GLD/SPY Volatility Ratio", "Stress Return Gap",
]
FINAL_METRIC = "Final Gold Diversification Score"
SOURCE_PATHS = {
    "gold_diversification_score": str(SCORE_FILE),
    "allocation_history": str(HISTORY_FILE),
    "data_quality_report": str(QUALITY_FILE),
    "decision_rules": "scripts/gold_decision_rules.py",
    "allocation_rules": "scripts/gold_utils.py",
}
BOUNDARY_READER_WARNINGS = (
    "Nextafter values are technical rule-boundary values.",
    "A stress gap just above zero may be economically indistinguishable from zero.",
    (
        "Reaching a higher allocation range demonstrates existing rule mechanics, "
        "not a robust allocation recommendation."
    ),
    "Economic materiality and buffer robustness have not been established.",
)


class SourceError(RuntimeError):
    def __init__(
        self,
        message: str,
        ticker_latest_dates: dict[str, str | None] | None = None,
    ):
        super().__init__(message)
        self.ticker_latest_dates = ticker_latest_dates


def number(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise SourceError(f"Invalid numeric value for {label}") from error
    if not math.isfinite(result):
        raise SourceError(f"Non-finite numeric value for {label}")
    return result


def date_text(value: Any, label: str) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise SourceError(f"Invalid date for {label}")
    return pd.Timestamp(parsed).date().isoformat()


def read_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    if not path.exists():
        raise SourceError(f"Missing required source: {path}")
    try:
        frame = pd.read_csv(path)
    except Exception as error:
        raise SourceError(
            f"Unreadable required source: {path} ({type(error).__name__})"
        ) from error
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise SourceError(f"Incompatible required source: {path}; missing {missing}")
    if frame.empty:
        raise SourceError(f"Empty required source: {path}")
    return frame


def empty_output() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_readiness": {
            "status": "blocked",
            "blocking_issues": [],
            "review_warnings": [],
        },
        "dates": {
            "score_source_as_of_date": None,
            "allocation_history_source_period_label": None,
            "core_market_data_as_of_date": None,
            "all_tracked_market_data_as_of_date": None,
            "ticker_latest_dates": {},
        },
        "observed_score_engine": {},
        "observed_allocation_history": {},
        "decision_limits": {},
        "score_engine_threshold_information": None,
        "allocation_guidance_rule_information": None,
        "score_engine_scenarios": [],
        "allocation_history_style_scenarios": [],
        "source_report_paths": SOURCE_PATHS,
        "methodology_note": "Scenario fields are conditional and non-predictive.",
    }


def write_output(payload: dict[str, Any]) -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def read_dates(warnings: list[str]) -> tuple[dict[str, Any], str]:
    quality = read_csv(QUALITY_FILE, QUALITY_COLUMNS)
    ticker_dates: dict[str, str | None] = {}
    all_valid: list[str] = []
    core_dates: list[str] = []
    seen: set[str] = set()

    for _, row in quality.iterrows():
        ticker = str(row["Ticker"]).strip()
        if not ticker:
            raise SourceError(f"Blank ticker in {QUALITY_FILE}")
        if ticker in seen:
            raise SourceError(f"Duplicate ticker in {QUALITY_FILE}: {ticker}")
        seen.add(ticker)
        status = str(row["Status"]).strip()
        latest = None
        if not pd.isna(row["Latest Date"]):
            try:
                latest = date_text(row["Latest Date"], f"{ticker} latest date")
            except SourceError:
                latest = None
        ticker_dates[ticker] = latest
        if status == "Passed" and latest is None:
            raise SourceError(
                f"Passed ticker has invalid or missing Latest Date: {ticker}",
                ticker_latest_dates=dict(ticker_dates),
            )
        if status != "Failed" and latest is not None:
            all_valid.append(latest)
        if ticker in CORE_TICKERS:
            if status == "Failed":
                raise SourceError(
                    f"Core ticker failed data quality: {ticker}",
                    ticker_latest_dates=dict(ticker_dates),
                )
            if status != "Passed":
                warnings.append(f"Core ticker data quality is {status}: {ticker}")
            if latest is not None:
                core_dates.append(latest)
        elif status != "Passed":
            warnings.append(f"Additional tracked ticker data quality is {status}: {ticker}")

    missing = sorted(CORE_TICKERS - seen)
    if missing or len(core_dates) != len(CORE_TICKERS) or not all_valid:
        raise SourceError(
            f"Missing valid core ticker dates: {missing}",
            ticker_latest_dates=dict(ticker_dates),
        )

    core_date = min(core_dates)
    return {
        "score_source_as_of_date": None,
        "allocation_history_source_period_label": None,
        "core_market_data_as_of_date": core_date,
        "all_tracked_market_data_as_of_date": min(all_valid),
        "ticker_latest_dates": ticker_dates,
    }, core_date


def metric_row(frame: pd.DataFrame, metric: str) -> pd.Series:
    rows = frame.loc[frame["Metric"] == metric]
    if len(rows) != 1:
        raise SourceError(f"Expected one metric row for {metric}")
    return rows.iloc[0]


def score_engine_result(inputs: dict[str, float]) -> dict[str, Any]:
    component_scores = {
        "Correlation Score": score_correlation(
            inputs["average_gld_equity_correlation"]
        ),
        "Volatility Score": score_volatility_ratio(
            inputs["gld_spy_volatility_ratio"]
        ),
        "Stress Performance Score": score_stress_gap(inputs["stress_return_gap"]),
        "Risk Contribution Score": score_risk_contribution(
            inputs["gld_risk_contribution"]
        ),
    }
    return {
        "inputs": dict(inputs),
        "component_scores": component_scores,
        "final_score": calculate_final_score(component_scores),
    }


def read_score_engine(warnings: list[str]) -> tuple[dict[str, Any], dict[str, float]]:
    score = read_csv(SCORE_FILE, SCORE_COLUMNS)
    inputs: dict[str, float] = {}
    components = []
    metadata = score_engine_metadata()
    for component in metadata:
        row = metric_row(score, component["metric"])
        value = number(row["Value"], component["metric"])
        observed_score = number(row["Score"], component["metric"])
        inputs[component["field"]] = value
        components.append({
            "metric": component["metric"],
            "field": component["field"],
            "score_label": component["score_label"],
            "value": value,
            "score": observed_score,
            "weight": component["weight"],
            "source_report_path": str(SCORE_FILE),
        })

    calculated = score_engine_result(inputs)
    for component in components:
        calculated_score = calculated["component_scores"][component["score_label"]]
        if not math.isclose(
            component["score"], calculated_score, rel_tol=0, abs_tol=1e-12
        ):
            raise SourceError(
                f"Score component formula parity failure: {component['metric']}"
            )

    final_row = metric_row(score, FINAL_METRIC)
    final_score = number(final_row["Score"], FINAL_METRIC)
    if not math.isclose(
        final_score, calculated["final_score"], rel_tol=0, abs_tol=1e-12
    ):
        raise SourceError("Final score formula parity failure")

    warnings.append(
        "gold_diversification_score.csv lacks intrinsic date metadata; "
        "gold_diversification_score.source_as_of_date is null."
    )
    return {
        "source_type": "observed",
        "source_as_of_date": None,
        "source_report_path": str(SCORE_FILE),
        "components": components,
        "final_score": final_score,
        "weights": {
            component["field"]: component["weight"] for component in components
        },
    }, inputs


def read_history(
    core_date: str, warnings: list[str]
) -> tuple[dict[str, Any], dict[str, float], str]:
    history = read_csv(HISTORY_FILE, HISTORY_COLUMNS).copy()
    history["_date"] = pd.to_datetime(history["Date"], errors="coerce")
    if history["_date"].isna().any() or history["_date"].duplicated().any():
        raise SourceError(f"Invalid history dates in {HISTORY_FILE}")
    latest = history.sort_values("_date").iloc[-1]
    label = pd.Timestamp(latest["_date"]).date().isoformat()
    if label > core_date:
        warnings.append(
            "allocation_history_period_label is later than "
            "core_market_data_as_of_date; it is a period-end label, not observed data "
            "coverage."
        )

    inputs = {
        "average_gld_equity_correlation": number(
            latest["Average GLD-Equity Correlation"], "history correlation"
        ),
        "gld_spy_volatility_ratio": number(
            latest["GLD/SPY Volatility Ratio"], "history volatility ratio"
        ),
        "stress_return_gap": number(
            latest["Stress Return Gap"], "history stress gap"
        ),
    }
    corr, vol, stress = calculate_history_component_scores(
        inputs["average_gld_equity_correlation"],
        inputs["gld_spy_volatility_ratio"],
        inputs["stress_return_gap"],
    )
    historical_score = calculate_history_gold_score(corr, vol, stress)
    observed_score = number(latest["Gold Diversification Score"], "history gold score")
    if not math.isclose(
        historical_score, observed_score, rel_tol=0, abs_tol=1e-12
    ):
        raise SourceError("Allocation-history formula parity failure")
    trace = allocation_rule_trace(
        observed_score,
        inputs["stress_return_gap"],
        inputs["average_gld_equity_correlation"],
        inputs["gld_spy_volatility_ratio"],
    )
    parity_fields = {
        "Allocation Guidance Score": trace["allocation_guidance_score"],
        "Alert Level": trace["alert_level"],
        "Recommendation Confidence": trace["recommendation_confidence"],
        "Best Marginal Step": trace["best_marginal_step"],
        "Recommended Strategic Range": trace["recommended_strategic_range"],
        "Status": score_status(observed_score),
    }
    for column, expected in parity_fields.items():
        observed = latest[column]
        if isinstance(expected, (int, float)):
            if not math.isclose(
                number(observed, column), expected, rel_tol=0, abs_tol=1e-12
            ):
                raise SourceError(f"Allocation-history parity failure: {column}")
        elif str(observed) != expected:
            raise SourceError(f"Allocation-history parity failure: {column}")

    return {
        "source_type": "observed_period_labelled",
        "source_as_of_date": None,
        "source_period_label": label,
        "source_report_path": str(HISTORY_FILE),
        "metrics": {
            **inputs,
            "historical_gold_score": observed_score,
            "status": str(latest["Status"]),
            "alert_level": str(latest["Alert Level"]),
            "allocation_guidance_score": number(
                latest["Allocation Guidance Score"], "allocation guidance score"
            ),
            "recommendation_confidence": str(latest["Recommendation Confidence"]),
            "best_marginal_step": str(latest["Best Marginal Step"]),
            "recommended_strategic_range": str(
                latest["Recommended Strategic Range"]
            ),
        },
        "allocation_guidance_rule_trace": trace,
    }, inputs, label


def decision_limits(observed: dict[str, Any]) -> dict[str, Any]:
    components = observed["components"]
    low_score = min(item["score"] for item in components)
    drags = [
        {**item, "weighted_drag": item["weight"] * (100 - item["score"])}
        for item in components
    ]
    high_drag = max(item["weighted_drag"] for item in drags)
    return {
        "lowest_component_score": {
            "score": low_score,
            "components": [item for item in components if item["score"] == low_score],
        },
        "largest_weighted_drag": {
            "weighted_drag": high_drag,
            "components": [
                item for item in drags if item["weighted_drag"] == high_drag
            ],
            "definition": (
                "existing component weight × (100 − existing component score)"
            ),
        },
    }


def direction_from_observed(observed: float, hypothetical: float) -> str:
    if hypothetical > observed:
        return "increase"
    if hypothetical < observed:
        return "decrease"
    return "unchanged"


def display_condition(boundary: dict[str, Any]) -> str:
    value = boundary["threshold"]
    operator_text = {
        "<": "略低于",
        ">": "略高于",
        "<=": "等于或低于",
        ">=": "等于或高于",
    }[boundary["operator"]]
    return f"{operator_text} {value:.2f}"


def just_inside(boundary: dict[str, Any]) -> float:
    threshold = boundary["threshold"]
    if boundary["operator"] == "<":
        return math.nextafter(threshold, -math.inf)
    if boundary["operator"] == ">":
        return math.nextafter(threshold, math.inf)
    return threshold


def changed_input(
    field: str, observed: float, hypothetical: float, boundary: dict[str, Any]
) -> dict[str, Any]:
    return {
        "scenario_type": "hypothetical_not_observed",
        "conditional_non_predictive": True,
        "field": field,
        "observed_value": observed,
        "hypothetical_value": hypothetical,
        "direction_from_observed": direction_from_observed(observed, hypothetical),
        "display_condition": display_condition(boundary),
        "authoritative_boundary": {
            "id": boundary["id"],
            "operator": boundary["operator"],
            "threshold": boundary["threshold"],
            "description": boundary["description"],
        },
    }


def boundary_reader_safety_metadata() -> dict[str, Any]:
    return {
        "technical_rule_boundary_test": True,
        "economic_materiality_assessed": False,
        "robustness_buffer_tested": False,
        "reader_warnings": list(BOUNDARY_READER_WARNINGS),
    }


def history_scenario(inputs: dict[str, float]) -> dict[str, Any]:
    corr, vol, stress = calculate_history_component_scores(
        inputs["average_gld_equity_correlation"],
        inputs["gld_spy_volatility_ratio"],
        inputs["stress_return_gap"],
    )
    score = calculate_history_gold_score(corr, vol, stress)
    return {
        "inputs": dict(inputs),
        "component_scores": {
            "correlation": corr,
            "volatility": vol,
            "stress": stress,
        },
        "historical_gold_score": score,
        "allocation_guidance_rule_trace": allocation_rule_trace(
            score,
            inputs["stress_return_gap"],
            inputs["average_gld_equity_correlation"],
            inputs["gld_spy_volatility_ratio"],
        ),
    }


def range_rule(rules: dict[str, Any], rule_id: str) -> dict[str, Any]:
    return next(item for item in rules["strategic_ranges"] if item["id"] == rule_id)


def predicate(rule: dict[str, Any], predicate_id: str) -> dict[str, Any]:
    return next(item for item in rule["predicates"] if item["id"] == predicate_id)


def next_higher_range(
    current_range: str, rules: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None]:
    order = list(rules["range_order"])
    if current_range not in order:
        raise SourceError(f"Unknown strategic range: {current_range}")
    index = order.index(current_range)
    if index == len(order) - 1:
        return None, None
    target = order[index + 1]
    return target, next(
        item for item in rules["strategic_ranges"] if item["range"] == target
    )


def predicate_results(
    scenario_result: dict[str, Any], target_rule: dict[str, Any] | None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if target_rule is None:
        return [], []
    trace = scenario_result["allocation_guidance_rule_trace"]
    results = trace["range_conditions"][target_rule["id"]]
    values = {
        **scenario_result["inputs"],
        "avg_corr": scenario_result["inputs"]["average_gld_equity_correlation"],
        "vol_ratio": scenario_result["inputs"]["gld_spy_volatility_ratio"],
        "stress_gap": scenario_result["inputs"]["stress_return_gap"],
        "score": scenario_result["historical_gold_score"],
    }
    satisfied = []
    failing = []
    for item in target_rule["predicates"]:
        detail = {
            "predicate_id": item["id"],
            "field": item["field"],
            "actual_value": values[item["field"]],
            "operator": item["operator"],
            "threshold": item["threshold"],
            "description": item["description"],
        }
        (satisfied if results[item["id"]] else failing).append(detail)
    return satisfied, failing


def allocation_scenario(
    scenario_id: str,
    scenario_category: str,
    changed: list[dict[str, Any]],
    inputs: dict[str, float],
    baseline_score: float,
    baseline_range: str,
    rules: dict[str, Any],
    rationale: str,
    construction_method: str,
    candidate_selection: dict[str, Any] | None = None,
    reader_safety: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = history_scenario(inputs)
    resulting_range = result["allocation_guidance_rule_trace"][
        "recommended_strategic_range"
    ]
    target_range, target_rule = next_higher_range(baseline_range, rules)
    order = list(rules["range_order"])
    if target_range is None:
        outcome_status = "not_applicable"
    elif order.index(resulting_range) >= order.index(target_range):
        outcome_status = "reaches_next_higher_range"
    else:
        outcome_status = "does_not_reach_next_higher_range"
    satisfied, failing = predicate_results(result, target_rule)
    payload = {
        "scenario_id": scenario_id,
        "scenario_category": scenario_category,
        "scenario_type": "hypothetical_not_observed",
        "conditional_non_predictive": True,
        "changed_inputs": changed,
        "changed_input_count": len(changed),
        "direction_from_observed": {
            item["field"]: item["direction_from_observed"] for item in changed
        },
        "scenario_rationale": rationale,
        "construction_method": construction_method,
        "candidate_selection": candidate_selection,
        "baseline_historical_score": baseline_score,
        "resulting_historical_score": result["historical_gold_score"],
        "baseline_range": baseline_range,
        "resulting_range": resulting_range,
        "next_higher_range": target_range,
        "target_rule": target_rule,
        "outcome_status": outcome_status,
        "satisfied_predicates": satisfied,
        "failing_predicates": failing,
        "result": result,
        "display_note": "条件性边界测试，不是预测，也不表示该情景将发生。",
    }
    if reader_safety is not None:
        payload["reader_safety"] = reader_safety
    return payload


def build_score_engine_scenarios(
    inputs: dict[str, float], baseline_score: float
) -> list[dict[str, Any]]:
    scenarios = []
    for component in score_engine_metadata():
        target_id = component["scenario_target_id"]
        if target_id is None:
            continue
        boundary = next(
            item
            for item in component["display_thresholds"]
            if item.get("id") == target_id
        )
        target = just_inside(boundary)
        scenario_inputs = inputs.copy()
        scenario_inputs[component["field"]] = target
        change = changed_input(
            component["field"], inputs[component["field"]], target, boundary
        )
        result = score_engine_result(scenario_inputs)
        scenarios.append({
            "scenario_id": f"score_engine_{target_id}",
            "scenario_type": "hypothetical_not_observed",
            "conditional_non_predictive": True,
            "changed_inputs": [change],
            "direction_from_observed": {
                component["field"]: change["direction_from_observed"]
            },
            "scenario_rationale": boundary["description"],
            "baseline_final_score": baseline_score,
            "resulting_final_score": result["final_score"],
            "observed_risk_contribution_treatment": {
                "status": "held_constant_observed",
                "value": inputs["gld_risk_contribution"],
            },
            "reader_safety": boundary_reader_safety_metadata(),
            "result": result,
            "display_note": "条件性分数引擎测试，不是配置区间结论或预测。",
        })
    return scenarios


def build_minimal_next_range_transition(
    inputs: dict[str, float], rules: dict[str, Any]
) -> dict[str, Any]:
    baseline_result = history_scenario(inputs)
    baseline_score = baseline_result["historical_gold_score"]
    baseline_range = baseline_result["allocation_guidance_rule_trace"][
        "recommended_strategic_range"
    ]
    target_range, target_rule = next_higher_range(baseline_range, rules)

    if target_rule is None:
        return allocation_scenario(
            "allocation_minimal_next_range_transition",
            "minimal_next_range_transition",
            [],
            inputs.copy(),
            baseline_score,
            baseline_range,
            rules,
            "The observed range is already the maximum authoritative range.",
            "not_applicable_current_range_is_maximum",
            {
                "minimal_definition": "fewest changed observed input fields",
                "tie_breaker": None,
                "evaluated_candidate_count": 0,
                "minimum_reaching_candidate_count": 0,
            },
            None,
        )

    baseline_conditions = baseline_result["allocation_guidance_rule_trace"][
        "range_conditions"
    ][target_rule["id"]]
    protected_fields: set[str] = set()
    direct_failures: list[dict[str, Any]] = []
    derived_dependencies: dict[str, str] = {}

    for target_predicate in target_rule["predicates"]:
        dependency = target_predicate["dependency"]
        is_satisfied = baseline_conditions[target_predicate["id"]]
        if dependency["type"] == "input":
            input_field = dependency["input_field"]
            if is_satisfied:
                protected_fields.add(input_field)
            else:
                direct_failures.append(target_predicate)
        elif not is_satisfied:
            for item in dependency["input_fields"]:
                derived_dependencies[item["input_field"]] = item[
                    "favorable_direction"
                ]

    candidates_by_field: dict[str, list[dict[str, Any]]] = {}

    def add_candidate(input_field: str, boundary: dict[str, Any]) -> None:
        target = just_inside(boundary)
        if target == inputs[input_field]:
            return
        candidate = {"field": input_field, "boundary": boundary, "target": target}
        existing = candidates_by_field.setdefault(input_field, [])
        identity = (boundary["operator"], boundary["threshold"], target)
        if not any(
            (item["boundary"]["operator"], item["boundary"]["threshold"], item["target"])
            == identity
            for item in existing
        ):
            existing.append(candidate)

    for target_predicate in direct_failures:
        add_candidate(
            target_predicate["dependency"]["input_field"], target_predicate
        )

    for input_field, favorable_direction in derived_dependencies.items():
        if input_field in protected_fields:
            continue
        for range_metadata in rules["strategic_ranges"]:
            for boundary in range_metadata["predicates"]:
                dependency = boundary["dependency"]
                if (
                    dependency["type"] != "input"
                    or dependency["input_field"] != input_field
                ):
                    continue
                target = just_inside(boundary)
                observed = inputs[input_field]
                improves = (
                    favorable_direction == "decrease" and target < observed
                ) or (
                    favorable_direction == "increase" and target > observed
                )
                if improves:
                    add_candidate(input_field, boundary)

    for field_candidates in candidates_by_field.values():
        field_candidates.sort(
            key=lambda item: (
                item["boundary"]["id"],
                item["boundary"]["operator"],
                item["target"],
            )
        )

    order = list(rules["range_order"])
    target_rank = order.index(target_range)
    evaluated: list[dict[str, Any]] = []
    reaching_at_minimum: list[dict[str, Any]] = []
    fields = sorted(candidates_by_field)

    for changed_count in range(1, len(fields) + 1):
        for selected_fields in combinations(fields, changed_count):
            option_groups = [candidates_by_field[field] for field in selected_fields]
            for selected_adjustments in product(*option_groups):
                scenario_inputs = inputs.copy()
                for adjustment in selected_adjustments:
                    scenario_inputs[adjustment["field"]] = adjustment["target"]
                result = history_scenario(scenario_inputs)
                result_range = result["allocation_guidance_rule_trace"][
                    "recommended_strategic_range"
                ]
                candidate = {
                    "adjustments": list(selected_adjustments),
                    "inputs": scenario_inputs,
                    "result": result,
                    "result_range": result_range,
                }
                evaluated.append(candidate)
                if order.index(result_range) >= target_rank:
                    reaching_at_minimum.append(candidate)
        if reaching_at_minimum:
            break

    def candidate_signature(candidate: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(
            (
                item["field"],
                item["boundary"]["id"],
                item["boundary"]["operator"],
                item["target"],
            )
            for item in candidate["adjustments"]
        )

    if reaching_at_minimum:
        selected = min(reaching_at_minimum, key=candidate_signature)
        selection_method = "minimum_changed_fields_reaching_next_range"
    elif evaluated:
        selected = min(
            evaluated,
            key=lambda item: (
                -order.index(item["result_range"]),
                -item["result"]["historical_gold_score"],
                len(item["adjustments"]),
                candidate_signature(item),
            ),
        )
        selection_method = "best_deterministic_non_reaching_candidate"
    else:
        selected = {
            "adjustments": [],
            "inputs": inputs.copy(),
            "result": baseline_result,
            "result_range": baseline_range,
        }
        selection_method = "no_authoritative_candidate_available"

    changes = [
        changed_input(
            item["field"], inputs[item["field"]], item["target"], item["boundary"]
        )
        for item in selected["adjustments"]
    ]
    return allocation_scenario(
        "allocation_minimal_next_range_transition",
        "minimal_next_range_transition",
        changes,
        selected["inputs"],
        baseline_score,
        baseline_range,
        rules,
        (
            f"Targets the authoritative next range {target_range}, preserves observed "
            "inputs whose direct target predicates already pass, and defines minimal as "
            "the fewest changed observed input fields."
        ),
        "authoritative_candidate_search",
        {
            "minimal_definition": "fewest changed observed input fields",
            "selection_method": selection_method,
            "tie_breaker": (
                "lexicographic by input field, predicate ID, operator, and machine target"
            ),
            "evaluated_candidate_count": len(evaluated),
            "minimum_reaching_candidate_count": len(reaching_at_minimum),
            "selected_candidate_signature": candidate_signature(selected),
            "protected_satisfied_input_fields": sorted(protected_fields),
        },
        boundary_reader_safety_metadata() if changes else None,
    )


def build_allocation_scenarios(
    inputs: dict[str, float], baseline_score: float, baseline_range: str
) -> list[dict[str, Any]]:
    rules = allocation_rule_metadata()
    rule_5_to_10 = range_rule(rules, "supports_5_to_10")
    rule_5_to_15 = range_rule(rules, "supports_5_to_15")
    boundaries = (
        (
            "allocation_correlation_boundary_proximity",
            "non_minimal_boundary_proximity",
            "average_gld_equity_correlation",
            predicate(rule_5_to_10, "average_correlation_below_0_70"),
            "Tests proximity to the authoritative correlation boundary; this is not the minimal transition scenario.",
        ),
        (
            "allocation_volatility_boundary",
            "single_authoritative_boundary",
            "gld_spy_volatility_ratio",
            predicate(rule_5_to_15, "volatility_ratio_below_1_80"),
            "Tests the authoritative strict volatility boundary while holding other observed inputs constant.",
        ),
        (
            "allocation_stress_boundary",
            "single_authoritative_boundary",
            "stress_return_gap",
            predicate(rule_5_to_10, "stress_gap_positive"),
            "Tests the authoritative strict stress-gap boundary while holding other observed inputs constant.",
        ),
    )
    scenarios = []
    for scenario_id, category, field, boundary, rationale in boundaries:
        target = just_inside(boundary)
        scenario_inputs = inputs.copy()
        scenario_inputs[field] = target
        scenarios.append(allocation_scenario(
            scenario_id,
            category,
            [changed_input(field, inputs[field], target, boundary)],
            scenario_inputs,
            baseline_score,
            baseline_range,
            rules,
            rationale,
            "single_authoritative_boundary",
            None,
            boundary_reader_safety_metadata(),
        ))

    scenarios.append(build_minimal_next_range_transition(inputs, rules))
    return scenarios


def build_output() -> dict[str, Any]:
    warnings: list[str] = []
    dates, core_date = read_dates(warnings)
    observed_score, score_inputs = read_score_engine(warnings)
    observed_history, history_inputs, label = read_history(core_date, warnings)
    dates["allocation_history_source_period_label"] = label
    baseline_range = observed_history["metrics"]["recommended_strategic_range"]
    baseline_history_score = observed_history["metrics"]["historical_gold_score"]
    allocation_rules = allocation_rule_metadata()

    return {
        "schema_version": SCHEMA_VERSION,
        "analysis_readiness": {
            "status": "needs_review" if warnings else "ready",
            "blocking_issues": [],
            "review_warnings": list(dict.fromkeys(warnings)),
        },
        "dates": dates,
        "observed_score_engine": observed_score,
        "observed_allocation_history": observed_history,
        "decision_limits": decision_limits(observed_score),
        "score_engine_threshold_information": {
            "source": "scripts/gold_decision_rules.py",
            "components": score_engine_metadata(),
        },
        "allocation_guidance_rule_information": {
            "source": "scripts/gold_utils.py",
            "authoritative_rule_specification": allocation_rules,
        },
        "score_engine_scenarios": build_score_engine_scenarios(
            score_inputs, observed_score["final_score"]
        ),
        "allocation_history_style_scenarios": build_allocation_scenarios(
            history_inputs, baseline_history_score, baseline_range
        ),
        "source_report_paths": SOURCE_PATHS,
        "methodology_note": (
            "Observed facts retain their source/date semantics. Score-engine and "
            "allocation-history-style scenarios use separate authoritative rule systems. "
            "All scenario results are conditional, deterministic, "
            "hypothetical_not_observed, and non-predictive. Nextafter and exact-boundary "
            "values are technical rule-boundary values. A stress gap just above zero may "
            "be economically indistinguishable from zero. Reaching a higher allocation "
            "range demonstrates existing rule mechanics, not a robust allocation "
            "recommendation. Economic materiality and buffer robustness have not been "
            "established."
        ),
    }


def main() -> None:
    try:
        output = build_output()
    except SourceError as error:
        output = empty_output()
        output["analysis_readiness"]["blocking_issues"] = [str(error)]
        if error.ticker_latest_dates is not None:
            output["dates"]["ticker_latest_dates"] = error.ticker_latest_dates
        write_output(output)
        print(
            f"Blocked decision-boundary explorer written to {OUTPUT_FILE}: {error}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    except Exception as error:
        output = empty_output()
        output["analysis_readiness"]["blocking_issues"] = [
            f"Explorer failed: {type(error).__name__}: {error}"
        ]
        write_output(output)
        print(
            f"Blocked decision-boundary explorer written to {OUTPUT_FILE}: {error}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    write_output(output)
    print(f"Decision-boundary explorer written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
