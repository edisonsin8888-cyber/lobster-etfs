from pathlib import Path
from datetime import datetime
from typing import Any
import html
import json
import math
import os
import sys
import tempfile
import pandas as pd
import re

DOC_PATH = Path(
    "docs/dashboard.html"
)

DECISION_BOUNDARY_FILE = Path(
    "reports/07_ai_research/decision_boundary_explorer.json"
)
DECISION_BOUNDARY_SCHEMA_VERSION = "1.0.0"


class DecisionBoundaryValidationError(ValueError):
    """The decision-boundary artifact cannot safely be rendered."""


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DecisionBoundaryValidationError(f"{label} must be an object")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise DecisionBoundaryValidationError(f"{label} must be a list")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DecisionBoundaryValidationError(f"{label} must be a non-empty string")
    return value


def _require_finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DecisionBoundaryValidationError(f"{label} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise DecisionBoundaryValidationError(f"{label} must be a finite number")
    return result


def _require_string_list(value: Any, label: str, minimum_length: int = 0) -> list[str]:
    items = _require_list(value, label)
    if len(items) < minimum_length:
        raise DecisionBoundaryValidationError(
            f"{label} must contain at least {minimum_length} item(s)"
        )
    for index, item in enumerate(items):
        _require_text(item, f"{label}[{index}]")
    return items


def _require_component_list(
    value: Any, label: str, numeric_field: str
) -> list[dict[str, Any]]:
    items = _require_list(value, label)
    if not items:
        raise DecisionBoundaryValidationError(f"{label} must not be empty")
    for index, item in enumerate(items):
        component = _require_object(item, f"{label}[{index}]")
        _require_text(component.get("metric"), f"{label}[{index}].metric")
        _require_finite_number(
            component.get(numeric_field), f"{label}[{index}].{numeric_field}"
        )
    return items


def load_decision_boundary_explorer(path: Path) -> dict[str, Any]:
    """Load the direct explorer artifact; never use the packet's embedded copy."""
    if not path.exists():
        raise DecisionBoundaryValidationError(f"Explorer file is missing: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DecisionBoundaryValidationError(
            f"Explorer file cannot be parsed: {path} ({error})"
        ) from error
    return _require_object(payload, "explorer payload")


def select_minimal_transition(payload: dict[str, Any]) -> dict[str, Any]:
    scenarios = _require_list(
        payload.get("allocation_history_style_scenarios"),
        "allocation_history_style_scenarios",
    )
    matches = [
        scenario
        for scenario in scenarios
        if isinstance(scenario, dict)
        and scenario.get("scenario_category") == "minimal_next_range_transition"
    ]
    if len(matches) != 1:
        raise DecisionBoundaryValidationError(
            "allocation_history_style_scenarios must contain exactly one "
            "minimal_next_range_transition scenario"
        )
    return matches[0]


def _validate_changed_inputs(changed_inputs: list[Any]) -> None:
    for index, item in enumerate(changed_inputs):
        changed = _require_object(item, f"minimal transition changed_inputs[{index}]")
        _require_text(changed.get("field"), f"changed_inputs[{index}].field")
        _require_finite_number(
            changed.get("observed_value"), f"changed_inputs[{index}].observed_value"
        )
        _require_finite_number(
            changed.get("hypothetical_value"), f"changed_inputs[{index}].hypothetical_value"
        )
        _require_text(
            changed.get("direction_from_observed"),
            f"changed_inputs[{index}].direction_from_observed",
        )
        _require_text(
            changed.get("display_condition"),
            f"changed_inputs[{index}].display_condition",
        )
        if changed.get("scenario_type") != "hypothetical_not_observed":
            raise DecisionBoundaryValidationError(
                f"changed_inputs[{index}].scenario_type must be hypothetical_not_observed"
            )


def _validate_reader_safety(safety: Any) -> dict[str, Any]:
    safety = _require_object(safety, "minimal transition reader_safety")
    if safety.get("technical_rule_boundary_test") is not True:
        raise DecisionBoundaryValidationError(
            "reader_safety.technical_rule_boundary_test must be true"
        )
    if safety.get("economic_materiality_assessed") is not False:
        raise DecisionBoundaryValidationError(
            "reader_safety.economic_materiality_assessed must be false"
        )
    if safety.get("robustness_buffer_tested") is not False:
        raise DecisionBoundaryValidationError(
            "reader_safety.robustness_buffer_tested must be false"
        )
    _require_string_list(
        safety.get("reader_warnings"), "reader_safety.reader_warnings", minimum_length=4
    )
    return safety


def validate_decision_boundary_explorer(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Validate the display contract before the dashboard output is opened."""
    if payload.get("schema_version") != DECISION_BOUNDARY_SCHEMA_VERSION:
        raise DecisionBoundaryValidationError(
            "Unsupported explorer schema_version: "
            f"expected {DECISION_BOUNDARY_SCHEMA_VERSION!r}, "
            f"found {payload.get('schema_version')!r}"
        )

    readiness = _require_object(payload.get("analysis_readiness"), "analysis_readiness")
    status = readiness.get("status")
    if status == "blocked":
        raise DecisionBoundaryValidationError("Explorer analysis_readiness is blocked")
    if status not in {"ready", "needs_review"}:
        raise DecisionBoundaryValidationError(
            "analysis_readiness.status must be ready or needs_review"
        )
    _require_list(readiness.get("blocking_issues"), "analysis_readiness.blocking_issues")
    _require_string_list(
        readiness.get("review_warnings"), "analysis_readiness.review_warnings"
    )

    dates = _require_object(payload.get("dates"), "dates")
    _require_text(dates.get("core_market_data_as_of_date"), "dates.core_market_data_as_of_date")
    _require_text(
        dates.get("allocation_history_source_period_label"),
        "dates.allocation_history_source_period_label",
    )

    observed = _require_object(
        payload.get("observed_allocation_history"), "observed_allocation_history"
    )
    _require_text(observed.get("source_type"), "observed_allocation_history.source_type")
    _require_text(
        observed.get("source_period_label"),
        "observed_allocation_history.source_period_label",
    )
    observed_metrics = _require_object(
        observed.get("metrics"), "observed_allocation_history.metrics"
    )
    _require_finite_number(
        observed_metrics.get("historical_gold_score"),
        "observed_allocation_history.metrics.historical_gold_score",
    )
    _require_text(
        observed_metrics.get("recommended_strategic_range"),
        "observed_allocation_history.metrics.recommended_strategic_range",
    )

    limits = _require_object(payload.get("decision_limits"), "decision_limits")
    lowest = _require_object(limits.get("lowest_component_score"), "lowest_component_score")
    _require_finite_number(lowest.get("score"), "lowest_component_score.score")
    _require_component_list(
        lowest.get("components"), "lowest_component_score.components", "score"
    )
    largest = _require_object(limits.get("largest_weighted_drag"), "largest_weighted_drag")
    _require_finite_number(
        largest.get("weighted_drag"), "largest_weighted_drag.weighted_drag"
    )
    _require_component_list(
        largest.get("components"), "largest_weighted_drag.components", "weighted_drag"
    )

    scenario = select_minimal_transition(payload)
    if scenario.get("scenario_type") != "hypothetical_not_observed":
        raise DecisionBoundaryValidationError(
            "minimal transition scenario_type must be hypothetical_not_observed"
        )
    if scenario.get("conditional_non_predictive") is not True:
        raise DecisionBoundaryValidationError(
            "minimal transition conditional_non_predictive must be true"
        )
    for field in (
        "baseline_range",
        "resulting_range",
        "outcome_status",
        "construction_method",
    ):
        _require_text(scenario.get(field), f"minimal transition {field}")
    changed_inputs = _require_list(scenario.get("changed_inputs"), "minimal transition changed_inputs")
    changed_input_count = _require_finite_number(
        scenario.get("changed_input_count"), "minimal transition changed_input_count"
    )
    if not changed_input_count.is_integer() or int(changed_input_count) != len(changed_inputs):
        raise DecisionBoundaryValidationError(
            "minimal transition changed_input_count must match changed_inputs"
        )
    _require_object(
        scenario.get("direction_from_observed"),
        "minimal transition direction_from_observed",
    )
    _require_list(
        scenario.get("satisfied_predicates"), "minimal transition satisfied_predicates"
    )
    failing_predicates = _require_list(
        scenario.get("failing_predicates"), "minimal transition failing_predicates"
    )
    selection = _require_object(
        scenario.get("candidate_selection"), "minimal transition candidate_selection"
    )
    _require_text(selection.get("minimal_definition"), "minimal transition minimal_definition")
    _require_finite_number(
        selection.get("evaluated_candidate_count"),
        "minimal transition evaluated_candidate_count",
    )
    _require_finite_number(
        selection.get("minimum_reaching_candidate_count"),
        "minimal transition minimum_reaching_candidate_count",
    )
    _require_text(scenario.get("scenario_id"), "minimal transition scenario_id")
    _require_text(scenario.get("scenario_rationale"), "minimal transition scenario_rationale")
    _require_finite_number(
        scenario.get("baseline_historical_score"), "minimal transition baseline_historical_score"
    )
    _require_finite_number(
        scenario.get("resulting_historical_score"), "minimal transition resulting_historical_score"
    )
    _require_object(scenario.get("result"), "minimal transition result")
    _require_text(scenario.get("display_note"), "minimal transition display_note")

    next_higher_range = scenario.get("next_higher_range")
    outcome_status = scenario["outcome_status"]
    is_maximum = next_higher_range is None and outcome_status == "not_applicable"
    if next_higher_range is None and not is_maximum:
        raise DecisionBoundaryValidationError(
            "next_higher_range may be null only when outcome_status is not_applicable"
        )
    if outcome_status == "not_applicable" and next_higher_range is not None:
        raise DecisionBoundaryValidationError(
            "not_applicable outcome_status requires next_higher_range to be null"
        )

    if is_maximum:
        if scenario["resulting_range"] != scenario["baseline_range"]:
            raise DecisionBoundaryValidationError(
                "maximum-range scenario resulting_range must equal baseline_range"
            )
        if changed_inputs:
            raise DecisionBoundaryValidationError(
                "maximum-range scenario changed_inputs must be empty"
            )
        if failing_predicates:
            raise DecisionBoundaryValidationError(
                "maximum-range scenario failing_predicates must be empty"
            )
        if scenario.get("target_rule") is not None:
            raise DecisionBoundaryValidationError(
                "maximum-range scenario target_rule must be null"
            )
        if selection.get("tie_breaker") is not None:
            raise DecisionBoundaryValidationError(
                "maximum-range scenario tie_breaker must be null"
            )
        if "reader_safety" in scenario and scenario["reader_safety"] is not None:
            raise DecisionBoundaryValidationError(
                "maximum-range scenario must not provide regular reader_safety metadata"
            )
        return scenario, "not_applicable_maximum_range"

    _require_text(next_higher_range, "minimal transition next_higher_range")
    if outcome_status not in {
        "reaches_next_higher_range",
        "does_not_reach_next_higher_range",
    }:
        raise DecisionBoundaryValidationError(
            "regular transition outcome_status is not supported"
        )
    _require_object(scenario.get("target_rule"), "regular transition target_rule")
    _require_string_list(
        selection.get("protected_satisfied_input_fields"),
        "regular transition protected_satisfied_input_fields",
    )
    _require_text(selection.get("selection_method"), "regular transition selection_method")
    _require_text(selection.get("tie_breaker"), "regular transition tie_breaker")
    _validate_changed_inputs(changed_inputs)
    _validate_reader_safety(scenario.get("reader_safety"))
    return scenario, "regular_transition"


def format_display_number(value: Any) -> str:
    """Format only a validated JSON number; no score or threshold is recalculated."""
    number = _require_finite_number(value, "display value")
    if abs(number) >= 100:
        return f"{number:,.2f}"
    if abs(number) >= 1:
        return f"{number:,.2f}"
    return f"{number:.4f}"


def _escaped(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _render_components(components: list[dict[str, Any]], numeric_field: str) -> str:
    return "".join(
        "<li><strong>{metric}</strong>: {value}</li>".format(
            metric=_escaped(component["metric"]),
            value=_escaped(format_display_number(component[numeric_field])),
        )
        for component in components
    )


def _render_predicates(predicates: list[Any]) -> str:
    if not predicates:
        return "<li>None reported by the scenario.</li>"
    rendered = []
    for predicate in predicates:
        if isinstance(predicate, dict) and isinstance(predicate.get("description"), str):
            rendered.append(f"<li>{_escaped(predicate['description'])}</li>")
        else:
            rendered.append(f"<li>{_escaped(json.dumps(predicate, ensure_ascii=False))}</li>")
    return "".join(rendered)


def render_decision_boundary_section(payload: dict[str, Any]) -> str:
    """Render a static, escaped display from already-validated explorer fields."""
    scenario, scenario_mode = validate_decision_boundary_explorer(payload)
    readiness = payload["analysis_readiness"]
    dates = payload["dates"]
    observed = payload["observed_allocation_history"]
    metrics = observed["metrics"]
    limits = payload["decision_limits"]
    lowest = limits["lowest_component_score"]
    largest = limits["largest_weighted_drag"]
    selection = scenario["candidate_selection"]

    review_warnings = "".join(
        f"<li>{_escaped(warning)}</li>"
        for warning in readiness["review_warnings"]
    ) or "<li>No review warnings reported.</li>"
    changed_inputs = "".join(
        """
<li><strong>{field}</strong>: {direction}; {condition}
<details><summary>Machine boundary values (technical detail only)</summary>
Observed value: {observed_value}<br>
Hypothetical value: {hypothetical_value}
</details></li>
""".format(
            field=_escaped(item["field"]),
            direction=_escaped(item["direction_from_observed"]),
            condition=_escaped(item["display_condition"]),
            observed_value=_escaped(repr(float(item["observed_value"]))),
            hypothetical_value=_escaped(repr(float(item["hypothetical_value"]))),
        )
        for item in scenario["changed_inputs"]
    )

    if scenario_mode == "regular_transition":
        safety = scenario["reader_safety"]
        preserved_inputs = "".join(
            f"<li>{_escaped(field)}</li>"
            for field in selection["protected_satisfied_input_fields"]
        )
        reader_warnings = "".join(
            f"<li>{_escaped(warning)}</li>" for warning in safety["reader_warnings"]
        )
        hypothetical_section = f"""
<section class="decision-boundary-hypothetical" data-scenario-category="minimal_next_range_transition">
<h3>Hypothetical rule mechanics / 假设规则演示</h3>
<p><span class="decision-boundary-badge">hypothetical_not_observed</span><span class="decision-boundary-badge">conditional_non_predictive</span><span class="decision-boundary-badge">技术规则边界演示</span></p>
<div class="decision-boundary-grid">
<div class="decision-boundary-metric"><div class="title">Baseline range</div><div class="decision-boundary-value">{_escaped(scenario['baseline_range'])}</div></div>
<div class="decision-boundary-metric"><div class="title">Target range</div><div class="decision-boundary-value">{_escaped(scenario['next_higher_range'])}</div></div>
<div class="decision-boundary-metric"><div class="title">Resulting range</div><div class="decision-boundary-value">{_escaped(scenario['resulting_range'])}</div></div>
<div class="decision-boundary-metric"><div class="title">Outcome status</div><div class="decision-boundary-value">{_escaped(scenario['outcome_status'])}</div></div>
</div>
<div class="decision-boundary-details">
<p><strong>Changed inputs</strong></p><ul>{changed_inputs}</ul>
<p><strong>Preserved satisfied inputs</strong></p><ul>{preserved_inputs}</ul>
<p><strong>Failing predicates</strong></p><ul>{_render_predicates(scenario['failing_predicates'])}</ul>
<p>Construction method: {_escaped(scenario['construction_method'])}</p>
<p>Minimal definition: {_escaped(selection['minimal_definition'])}</p>
<p>Selection method: {_escaped(selection['selection_method'])}</p>
<p>Tie breaker: {_escaped(selection['tie_breaker'])}</p>
</div>
</section>

<section class="decision-boundary-safety">
<h3>Reader-safety warning / 阅读安全提示</h3>
<ul>{reader_warnings}</ul>
<p>technical_rule_boundary_test: {_escaped(safety['technical_rule_boundary_test'])}</p>
<p>economic_materiality_assessed: {_escaped(safety['economic_materiality_assessed'])}</p>
<p>robustness_buffer_tested: {_escaped(safety['robustness_buffer_tested'])}</p>
</section>
"""
    else:
        hypothetical_section = f"""
<section class="decision-boundary-hypothetical" data-scenario-category="minimal_next_range_transition" data-scenario-mode="not_applicable_maximum_range">
<h3>Hypothetical rule mechanics / 假设规则演示</h3>
<p><span class="decision-boundary-badge">conditional_non_predictive</span><span class="decision-boundary-badge">not_applicable</span></p>
<div class="decision-boundary-grid">
<div class="decision-boundary-metric"><div class="title">Baseline range</div><div class="decision-boundary-value">{_escaped(scenario['baseline_range'])}</div></div>
<div class="decision-boundary-metric"><div class="title">Resulting range</div><div class="decision-boundary-value">{_escaped(scenario['resulting_range'])}</div></div>
<div class="decision-boundary-metric"><div class="title">Outcome status</div><div class="decision-boundary-value">{_escaped(scenario['outcome_status'])}</div></div>
</div>
<div class="decision-boundary-details">
<p>当前规则体系没有更高配置区间，因此未生成下一档技术边界情景。</p>
<p>Construction method: {_escaped(scenario['construction_method'])}</p>
<p>Minimal definition: {_escaped(selection['minimal_definition'])}</p>
</div>
</section>

<section class="decision-boundary-safety">
<h3>Boundary test status / 边界测试状态</h3>
<p>未生成下一档边界情景。</p>
<p>未执行经济重要性或缓冲稳健性测试。</p>
</section>
"""

    return f"""
<div class="card decision-boundary-card">
<h2>Gold Decision Boundary</h2>

<section class="decision-boundary-observed">
<h3>Observed evidence / 已观察事实</h3>
<p class="decision-boundary-source">Source type: {_escaped(observed['source_type'])} (observed / observed_period_labelled)</p>
<div class="decision-boundary-grid">
<div class="decision-boundary-metric"><div class="title">Current allocation-history range</div><div class="decision-boundary-value">{_escaped(metrics['recommended_strategic_range'])}</div></div>
<div class="decision-boundary-metric"><div class="title">Current historical score</div><div class="decision-boundary-value">{_escaped(format_display_number(metrics['historical_gold_score']))}</div></div>
<div class="decision-boundary-metric"><div class="title">Lowest component score</div><div class="decision-boundary-value">{_escaped(format_display_number(lowest['score']))}</div></div>
<div class="decision-boundary-metric"><div class="title">Largest weighted drag</div><div class="decision-boundary-value">{_escaped(format_display_number(largest['weighted_drag']))}</div></div>
</div>
<div class="decision-boundary-details">
<p><strong>Lowest component(s), including ties</strong></p><ul>{_render_components(lowest['components'], 'score')}</ul>
<p><strong>Largest-drag component(s), including ties</strong></p><ul>{_render_components(largest['components'], 'weighted_drag')}</ul>
<p>Allocation source period label: {_escaped(observed['source_period_label'])}</p>
<p>Core market data as-of date: {_escaped(dates['core_market_data_as_of_date'])}</p>
<p>Analysis readiness: {_escaped(readiness['status'])}</p>
<p><strong>Review warnings</strong></p><ul>{review_warnings}</ul>
</div>
</section>

{hypothetical_section}
</div>
"""


def atomic_write_text(output_path: Path, content: str) -> None:
    """Durably replace an output file without exposing a partial dashboard."""
    output_path = Path(output_path)
    mode = 0o644
    if output_path.exists():
        mode = output_path.stat().st_mode & 0o777
    descriptor = None
    temporary_path = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), mode)
        os.replace(temporary_path, output_path)
        temporary_path = None
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def read_file(path):

    if path.exists():
        return path.read_text()

    return "No data available."


def read_score():

    path = Path(
        "reports/06_score_and_monitor/gold_diversification_score.csv"
    )

    if path.exists():

        df = pd.read_csv(path)

        numeric_cols = df.select_dtypes(
            include="number"
        ).columns

        if len(numeric_cols) > 0:

            return round(
                float(df.iloc[-1][numeric_cols[0]]),
                2
            )

    return "N/A"



def read_etf_scores():

    path = Path(
        "reports/07_lobster_watchlist/etf_score_table.csv"
    )

    if path.exists():

        df = pd.read_csv(path)

        return df.to_html(
            index=False,
            classes="table"
        )

    return "No ETF data"



def read_system_status():

    path = Path(
        "reports/08_agent_ops/lobster_system_status.txt"
    )

    if path.exists():

        text = path.read_text()

        if "Healthy" in text:
            return "Healthy"

    return "Unknown"



def read_market_focus():

    path = Path(
        "reports/07_lobster_watchlist/lobster_research_router.txt"
    )

    if path.exists():

        text = path.read_text()

        for line in text.splitlines():

            if "GLD" in line:
                return "GLD"

            if "XLK" in line:
                return "XLK"

            if "SPY" in line:
                return "SPY"

            if "QQQ" in line:
                return "QQQ"

            if "TLT" in line:
                return "TLT"

    return "N/A"



def read_etf_leader():

    path = Path(
        "reports/07_lobster_watchlist/etf_score_table.csv"
    )

    if path.exists():

        df = pd.read_csv(path)

        return str(
            df.iloc[0].iloc[0]
        )

    return "N/A"



def read_alert_status():

    path = Path(
        "reports/06_score_and_monitor/diversification_alert.txt"
    )

    if path.exists():

        text = path.read_text().upper()

        if "RED" in text:
            return "RED"

        if "YELLOW" in text:
            return "YELLOW"

        if "GREEN" in text:
            return "GREEN"

    return "N/A"


def read_allocation_range():

    path = Path(
        "reports/06_score_and_monitor/gold_signal_dashboard.txt"
    )

    if path.exists():

        text = path.read_text()

        for line in text.splitlines():

            if "Recommended Strategic Range" in line:

                return line.split(":")[-1].strip()


            if "Strategic Range" in line:

                return line.split(":")[-1].strip()


    return "N/A"

def read_ai_summary():

    summary = []


    # Gold defensive sleeve

    gold_path = Path(
        "reports/06_score_and_monitor/gold_signal_dashboard.txt"
    )


    if gold_path.exists():

        text = gold_path.read_text()

        for line in text.splitlines():

            if "Gold Diversification Score" in line:

                summary.append(line.strip())


            if "Allocation Stance" in line:

                summary.append(line.strip())



    # Growth sleeve

    xlk_path = Path(
        "reports/08_growth_sleeve/xlk_growth_monitor.txt"
    )


    if xlk_path.exists():

        text = xlk_path.read_text()

        for line in text.splitlines():

            if "Growth Sleeve Score" in line:

                summary.append(line.strip())


            if "Risk Flag" in line:

                summary.append(line.strip())



        # Router decision

    router_path = Path(
        "reports/07_lobster_watchlist/lobster_research_router.txt"
    )


    if router_path.exists():

        text = router_path.read_text()


        for ticker in [
            "GLD",
            "SPY",
            "QQQ",
            "XLK",
            "TLT"
        ]:

            if ticker in text:

                summary.append(
                    f"Next Deep-Dive Candidate: {ticker}"
                )

                break



    if summary:

        return "\n\n".join(summary)


    return (
        "AI analysis unavailable."
    )

def read_ai_commentary():

    path = Path(
        "reports/08_agent_ops/ai_portfolio_commentary.txt"
    )


    if path.exists():

        return path.read_text()


    return "AI commentary unavailable."

def read_metric_interpretation():

    path = Path(
        "reports/08_agent_ops/metric_interpretation.txt"
    )


    if path.exists():

        return path.read_text()


    return "Metric interpretation unavailable."

def generate_dashboard(
    explorer_path: Path = DECISION_BOUNDARY_FILE,
    output_path: Path = DOC_PATH,
):

    decision_boundary_payload = load_decision_boundary_explorer(Path(explorer_path))
    decision_boundary_section = render_decision_boundary_section(
        decision_boundary_payload
    )


    score = read_score()

    system_summary = read_system_status()

    market_focus = read_market_focus()

    etf_leader = read_etf_leader()

    alert_status = read_alert_status()

    allocation_range = read_allocation_range()

    metric_interpretation = read_metric_interpretation()

    ai_commentary = read_ai_commentary()

    ai_summary = read_ai_summary()


    system_status = read_file(
        Path(
            "reports/08_agent_ops/lobster_system_status.txt"
        )
    )


    risk_report = read_file(
        Path(
            "reports/06_score_and_monitor/ai_risk_monitor_report.txt"
        )
    )


    router = read_file(
        Path(
            "reports/07_lobster_watchlist/lobster_research_router.txt"
        )
    )


    memo = read_file(
        Path(
            "reports/07_lobster_watchlist/lobster_weekly_memo.txt"
        )
    )


    etf_table = read_etf_scores()

    html = f"""

    
<!DOCTYPE html>

<html>

<head>

<title>
AI-Powered ETF Research and Portfolio Intelligence Platform
</title>


<style>

body {{

font-family:
Arial, Helvetica, sans-serif;

background:#f5f7fa;

margin:40px;

color:#222;

}}


h1 {{

color:#1f4e79;

font-size:40px;

}}


.card {{

background:white;

padding:25px;

margin-top:25px;

border-radius:15px;

box-shadow:
0 3px 12px rgba(0,0,0,0.08);

max-width:1200px;

}}


.grid {{

display:grid;

grid-template-columns:
repeat(3,1fr);

gap:20px;

}}


.metric {{

background:#f8fbff;

padding:20px;

border-radius:15px;

text-align:center;

}}


.title {{

color:#555;

font-size:18px;

}}


.value {{

font-size:42px;

font-weight:bold;

color:#1f4e79;

margin-top:10px;

}}


pre {{

white-space:pre-wrap;

background:#fafafa;

padding:15px;

border-radius:10px;

line-height:1.5;

max-height:500px;

overflow-y:auto;

}}


.table-wrapper {{

overflow-x:auto;

width:100%;

}}


.table {{

width:max-content;

min-width:100%;

border-collapse:collapse;

font-size:14px;

}}


.table td,
.table th {{

padding:10px;

border-bottom:1px solid #ddd;

white-space:nowrap;

}}


.table td,
.table th {{

padding:10px;

border-bottom:1px solid #ddd;

}}


.decision-boundary-card {{

border-top:4px solid #1f4e79;

}}


.decision-boundary-observed,
.decision-boundary-hypothetical,
.decision-boundary-safety {{

padding:20px;

margin-top:18px;

border-radius:12px;

}}


.decision-boundary-observed {{

background:#f1f7fd;

border-left:5px solid #1f4e79;

}}


.decision-boundary-hypothetical {{

background:#fff8e7;

border-left:5px solid #b7791f;

}}


.decision-boundary-safety {{

background:#fff3f3;

border-left:5px solid #b83232;

}}


.decision-boundary-grid {{

display:grid;

grid-template-columns:repeat(2,1fr);

gap:15px;

}}


.decision-boundary-metric {{

background:white;

padding:15px;

border-radius:10px;

}}


.decision-boundary-value {{

font-size:24px;

font-weight:bold;

color:#1f4e79;

margin-top:8px;

}}


.decision-boundary-details {{

margin-top:15px;

}}


.decision-boundary-source {{

color:#555;

}}


.decision-boundary-badge {{

display:inline-block;

background:#8a5a00;

color:white;

padding:6px 9px;

margin:0 6px 6px 0;

border-radius:999px;

font-size:13px;

font-weight:bold;

}}


@media (max-width:800px) {{

.decision-boundary-grid {{

grid-template-columns:1fr;

}}

}}

</style>


</head>


<body>


<h1>
AI-Powered ETF Research and Portfolio Intelligence Platform
</h1>


<p>
Last Updated:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
</p>

<p>
An automated research system for ETF monitoring,
risk assessment, and portfolio allocation analysis.
</p>

<div class="card">

<h2>
Dashboard Summary
</h2>


<div class="grid">


<div class="metric">

<div class="title">
System Status
</div>

<div class="value">
{system_summary}
</div>


</div>



<div class="metric">

<div class="title">
Market Focus
</div>

<div class="value">
{market_focus}
</div>

</div>



<div class="metric">

<div class="title">
ETF Leader
</div>

<div class="value">
{etf_leader}
</div>

</div>


</div>

</div>


<div class="card">

<h2>
Portfolio Intelligence
</h2>


<div class="grid">


<div class="metric">

<div class="title">
Gold Diversification Score
</div>

<div class="value">
{score}
</div>

</div>


<div class="metric">

<div class="title">
Recommended Allocation
</div>

<div class="value">
{allocation_range}
</div>

</div>


<div class="metric">

<div class="title">
Alert Status
</div>

<div class="value">
{alert_status}
</div>

</div>


</div>

</div>

{decision_boundary_section}

<div class="card">

<h2>
Metric Interpretation
</h2>

<pre>
{metric_interpretation}
</pre>

</div>


<div class="card">

<h2>
AI Portfolio Commentary
</h2>

<pre>
{ai_commentary}
</pre>

</div>

<div class="card">

<h2>
System Health
</h2>

<pre>
{system_status}
</pre>

</div>



<div class="card">

<h2>
ETF Watchlist Ranking
</h2>

<div class="table-wrapper">

{etf_table}

</div>

</div>

    <div class="card">

<h2>
AI Risk Monitor
</h2>

<pre>
{risk_report}
</pre>

</div>



<div class="card">

<h2>
Research Router
</h2>

<pre>
{router}
</pre>

</div>



<div class="card">

<h2>
Weekly Research Memo
</h2>

<pre>
{memo}
</pre>

</div>



<div class="card">

<h2>
Charts
</h2>


<img 
src="../reports/06_score_and_monitor/gold_div_score_history.png"
width="800"
>


<img 
src="../reports/06_score_and_monitor/allocation_guidance_history.png"
width="800"
>


<img 
src="../reports/06_score_and_monitor/gld_risk_budget_curve.png"
width="800"
>


</div>



</body>

</html>

"""


    atomic_write_text(Path(output_path), html)


    print(
        "Dashboard generated successfully."
    )



def main(
    explorer_path: Path = DECISION_BOUNDARY_FILE,
    output_path: Path = DOC_PATH,
) -> int:
    try:
        generate_dashboard(explorer_path=explorer_path, output_path=output_path)
    except DecisionBoundaryValidationError as error:
        print(f"Dashboard not generated: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
