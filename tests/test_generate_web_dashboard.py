import copy
import html
import importlib.util
import io
import json
from pathlib import Path
import re
import stat
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "generate_web_dashboard.py"
SPEC = importlib.util.spec_from_file_location("generate_web_dashboard", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
DASHBOARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DASHBOARD)


def regular_scenario(
    baseline_range="0%–5%",
    next_higher_range="5%–10%",
    resulting_range="5%–10%",
):
    return {
        "scenario_id": "allocation_minimal_next_range_transition",
        "scenario_category": "minimal_next_range_transition",
        "scenario_type": "hypothetical_not_observed",
        "conditional_non_predictive": True,
        "changed_inputs": [
            {
                "scenario_type": "hypothetical_not_observed",
                "field": "stress_return_gap",
                "observed_value": -0.0001,
                "hypothetical_value": 5e-324,
                "direction_from_observed": "increase",
                "display_condition": "just above 0.00",
            }
        ],
        "changed_input_count": 1,
        "direction_from_observed": {"stress_return_gap": "increase"},
        "scenario_rationale": "Fixture only; no production rule is calculated here.",
        "construction_method": "authoritative_candidate_search",
        "candidate_selection": {
            "minimal_definition": "fewest changed observed input fields",
            "selection_method": "minimum_changed_fields_reaching_next_range",
            "tie_breaker": "lexicographic by input field",
            "evaluated_candidate_count": 1,
            "minimum_reaching_candidate_count": 1,
            "protected_satisfied_input_fields": ["average_gld_equity_correlation"],
        },
        "baseline_historical_score": 40.0,
        "resulting_historical_score": 50.0,
        "baseline_range": baseline_range,
        "resulting_range": resulting_range,
        "next_higher_range": next_higher_range,
        "target_rule": {"id": "fixture_target_rule"},
        "outcome_status": "reaches_next_higher_range",
        "satisfied_predicates": [],
        "failing_predicates": [],
        "result": {},
        "display_note": "Conditional fixture display note.",
        "reader_safety": {
            "technical_rule_boundary_test": True,
            "economic_materiality_assessed": False,
            "robustness_buffer_tested": False,
            "reader_warnings": [
                "Nextafter values are technical rule-boundary values.",
                "A stress gap just above zero may be economically indistinguishable from zero.",
                "Reaching a higher allocation range demonstrates existing rule mechanics.",
                "Economic materiality and buffer robustness have not been established.",
            ],
        },
    }


def maximum_range_scenario():
    return {
        "scenario_id": "allocation_minimal_next_range_transition",
        "scenario_category": "minimal_next_range_transition",
        "scenario_type": "hypothetical_not_observed",
        "conditional_non_predictive": True,
        "changed_inputs": [],
        "changed_input_count": 0,
        "direction_from_observed": {},
        "scenario_rationale": "The observed range is already the maximum authoritative range.",
        "construction_method": "not_applicable_current_range_is_maximum",
        "candidate_selection": {
            "minimal_definition": "fewest changed observed input fields",
            "tie_breaker": None,
            "evaluated_candidate_count": 0,
            "minimum_reaching_candidate_count": 0,
        },
        "baseline_historical_score": 60.0,
        "resulting_historical_score": 60.0,
        "baseline_range": "5%–15%",
        "resulting_range": "5%–15%",
        "next_higher_range": None,
        "target_rule": None,
        "outcome_status": "not_applicable",
        "satisfied_predicates": [],
        "failing_predicates": [],
        "result": {
            "inputs": {
                "average_gld_equity_correlation": 0.30,
                "gld_spy_volatility_ratio": 1.40,
                "stress_return_gap": 0.03,
            },
            "component_scores": {
                "correlation": 70.0,
                "volatility": 60.0,
                "stress": 80.0,
            },
            "historical_gold_score": 60.0,
            "allocation_guidance_rule_trace": {
                "alert_level": "Yellow",
                "alert_conditions": {
                    "red": {
                        "average_correlation_at_least_0_60": False,
                        "volatility_ratio_at_least_1_70": False,
                        "score_below_45": False,
                    },
                    "yellow": {
                        "average_correlation_at_least_0_30": True,
                        "volatility_ratio_at_least_1_20": True,
                        "score_below_70": True,
                    },
                },
                "allocation_guidance_score": 85,
                "allocation_adjustments": {
                    "stress_gap_positive": 15,
                    "average_correlation_below_0_45": 10,
                    "average_correlation_above_0_65": 0,
                    "volatility_ratio_below_1_50": 10,
                    "volatility_ratio_above_1_80": 0,
                    "score_at_least_60": 10,
                    "score_below_45": 0,
                },
                "recommended_strategic_range": "5%–15%",
                "range_conditions": {
                    "supports_5_to_15": {
                        "stress_gap_positive": True,
                        "score_at_least_55": True,
                        "average_correlation_below_0_60": True,
                        "volatility_ratio_below_1_80": True,
                    },
                    "supports_5_to_10": {
                        "stress_gap_positive": True,
                        "score_at_least_45": True,
                        "average_correlation_below_0_70": True,
                    },
                },
                "best_marginal_step": "0% to 5%",
                "recommendation_confidence": "High",
                "allocation_stance": "Supportive",
            },
        },
        "display_note": "Conditional fixture display note.",
    }


def explorer_payload(status="needs_review", scenario=None):
    return {
        "schema_version": "1.0.0",
        "analysis_readiness": {
            "status": status,
            "blocking_issues": [],
            "review_warnings": ["review warning"] if status == "needs_review" else [],
        },
        "dates": {
            "core_market_data_as_of_date": "2026-07-09",
            "allocation_history_source_period_label": "2026-07-31",
        },
        "observed_allocation_history": {
            "source_type": "observed_period_labelled",
            "source_period_label": "2026-07-31",
            "metrics": {
                "historical_gold_score": 40.0,
                "recommended_strategic_range": "0%–5%",
            },
        },
        "decision_limits": {
            "lowest_component_score": {
                "score": 38.0,
                "components": [{"metric": "Correlation", "score": 38.0}],
            },
            "largest_weighted_drag": {
                "weighted_drag": 18.0,
                "components": [{"metric": "Correlation", "weighted_drag": 18.0}],
            },
        },
        "allocation_history_style_scenarios": [scenario or regular_scenario()],
    }


class GenerateWebDashboardTests(unittest.TestCase):
    def dashboard_reader_patches(self):
        return patch.multiple(
            DASHBOARD,
            read_score=lambda: "62.07",
            read_system_status=lambda: "Healthy",
            read_market_focus=lambda: "GLD",
            read_etf_leader=lambda: "GLD",
            read_alert_status=lambda: "RED",
            read_allocation_range=lambda: "0%–5%",
            read_metric_interpretation=lambda: "Metric fixture",
            read_ai_commentary=lambda: "Commentary fixture",
            read_ai_summary=lambda: "Summary fixture",
            read_file=lambda path: "Report fixture",
            read_etf_scores=lambda: "<table><tr><td>ETF fixture</td></tr></table>",
        )

    def render(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            explorer = temporary / "explorer.json"
            output = temporary / "dashboard.html"
            explorer.write_text(json.dumps(payload), encoding="utf-8")
            with self.dashboard_reader_patches():
                DASHBOARD.generate_dashboard(explorer_path=explorer, output_path=output)
            return output.read_text(encoding="utf-8")

    def assert_failure_preserves_output(self, payload=None, raw=None):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            explorer = temporary / "explorer.json"
            output = temporary / "dashboard.html"
            output.write_text("existing dashboard", encoding="utf-8")
            before_mtime = output.stat().st_mtime_ns
            if raw is not None:
                explorer.write_text(raw, encoding="utf-8")
            elif payload is not None:
                explorer.write_text(json.dumps(payload), encoding="utf-8")
            with self.dashboard_reader_patches():
                with self.assertRaises(DASHBOARD.DecisionBoundaryValidationError):
                    DASHBOARD.generate_dashboard(explorer_path=explorer, output_path=output)
            self.assertEqual(output.read_text(encoding="utf-8"), "existing dashboard")
            self.assertEqual(output.stat().st_mtime_ns, before_mtime)

    def scenario(self, payload):
        return payload["allocation_history_style_scenarios"][0]

    def test_regular_and_intermediate_transitions_render(self):
        for label, scenario in (
            ("baseline", regular_scenario()),
            (
                "intermediate",
                regular_scenario("5%–10%", "5%–15%", "5%–15%"),
            ),
        ):
            with self.subTest(label=label):
                rendered = self.render(explorer_payload(scenario=scenario))
                self.assertIn(scenario["baseline_range"], rendered)
                self.assertIn(scenario["next_higher_range"], rendered)
                self.assertIn("技术规则边界演示", rendered)
                for warning in scenario["reader_safety"]["reader_warnings"]:
                    self.assertIn(warning, rendered)

    def test_maximum_range_contract_and_rendering(self):
        rendered = self.render(explorer_payload(scenario=maximum_range_scenario()))
        self.assertIn('data-scenario-mode="not_applicable_maximum_range"', rendered)
        self.assertIn("5%–15%", rendered)
        self.assertIn("not_applicable", rendered)
        self.assertIn("当前规则体系没有更高配置区间，因此未生成下一档技术边界情景。", rendered)
        self.assertIn("未执行经济重要性或缓冲稳健性测试。", rendered)
        self.assertNotIn("技术规则边界演示", rendered)
        self.assertNotIn("Changed inputs", rendered)
        self.assertNotIn("Machine boundary values", rendered)
        self.assertNotIn("Reader-safety warning", rendered)

    def test_invalid_transition_combinations_fail(self):
        cases = []
        payload = explorer_payload(scenario=maximum_range_scenario())
        self.scenario(payload)["outcome_status"] = "reaches_next_higher_range"
        cases.append(("null next range with regular outcome", payload))
        payload = explorer_payload()
        self.scenario(payload)["outcome_status"] = "not_applicable"
        cases.append(("not applicable with next range", payload))
        payload = explorer_payload(scenario=maximum_range_scenario())
        self.scenario(payload)["changed_inputs"] = [regular_scenario()["changed_inputs"][0]]
        cases.append(("maximum range with changed input", payload))
        payload = explorer_payload()
        del self.scenario(payload)["reader_safety"]
        cases.append(("regular transition without reader safety", payload))
        for label, payload in cases:
            with self.subTest(label=label):
                self.assert_failure_preserves_output(payload)

    def test_ready_needs_review_and_blocked_statuses(self):
        self.assertIn("Analysis readiness: ready", self.render(explorer_payload(status="ready")))
        self.assertIn("review warning", self.render(explorer_payload(status="needs_review")))
        self.assert_failure_preserves_output(explorer_payload(status="blocked"))

    def test_contract_field_errors_and_non_finite_values_fail(self):
        with self.subTest(label="missing explorer"):
            self.assert_failure_preserves_output()
        with self.subTest(label="malformed JSON"):
            self.assert_failure_preserves_output(raw="{")
        cases = []
        payload = explorer_payload()
        payload["schema_version"] = "9.9.9"
        cases.append(("unsupported schema", payload))
        payload = explorer_payload()
        del payload["dates"]["core_market_data_as_of_date"]
        cases.append(("missing date", payload))
        payload = explorer_payload()
        payload["decision_limits"]["lowest_component_score"]["components"] = []
        cases.append(("empty lowest ties", payload))
        payload = explorer_payload()
        payload["decision_limits"]["largest_weighted_drag"]["weighted_drag"] = True
        cases.append(("boolean drag", payload))
        payload = explorer_payload()
        del self.scenario(payload)["candidate_selection"]["selection_method"]
        cases.append(("missing selection method", payload))
        payload = explorer_payload()
        self.scenario(payload)["reader_safety"]["reader_warnings"] = ["only one"]
        cases.append(("short reader warnings", payload))
        payload = explorer_payload()
        payload["observed_allocation_history"]["metrics"]["historical_gold_score"] = float("nan")
        cases.append(("nan score", payload))
        payload = explorer_payload()
        self.scenario(payload)["changed_inputs"][0]["hypothetical_value"] = float("inf")
        cases.append(("infinite hypothetical value", payload))
        for label, payload in cases:
            with self.subTest(label=label):
                self.assert_failure_preserves_output(payload)

    def test_ties_html_escaping_and_exact_nextafter_details_location(self):
        payload = explorer_payload()
        payload["analysis_readiness"]["review_warnings"] = ["review <warning> & detail"]
        payload["decision_limits"]["lowest_component_score"]["components"].append(
            {"metric": "Lowest tie <metric>", "score": 38.0}
        )
        payload["decision_limits"]["largest_weighted_drag"]["components"].append(
            {"metric": "Largest tie <metric>", "weighted_drag": 18.0}
        )
        self.scenario(payload)["reader_safety"]["reader_warnings"] = [
            "reader <one> & alpha",
            "reader <two> & beta",
            "reader <three> & gamma",
            "reader <four> & delta",
        ]
        rendered = self.render(payload)
        self.assertIn("Lowest tie &lt;metric&gt;", rendered)
        self.assertIn("Largest tie &lt;metric&gt;", rendered)
        self.assertIn("review &lt;warning&gt; &amp; detail", rendered)
        for warning in self.scenario(payload)["reader_safety"]["reader_warnings"]:
            self.assertIn(html.escape(warning), rendered)
        stress_details = re.search(
            r"<li><strong>stress_return_gap</strong>.*?<details>.*?Hypothetical value: 5e-324.*?</details>",
            rendered,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(stress_details)
        without_details = re.sub(r"<details>.*?</details>", "", rendered, flags=re.DOTALL)
        self.assertNotIn("5e-324", without_details)

    def test_atomic_write_success_and_failure_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "dashboard.html"
            output.write_text("old", encoding="utf-8")
            output.chmod(0o600)
            DASHBOARD.atomic_write_text(output, "new")
            self.assertEqual(output.read_text(encoding="utf-8"), "new")
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)

            output.write_text("stable", encoding="utf-8")
            before_mtime = output.stat().st_mtime_ns
            with patch.object(DASHBOARD.os, "replace", side_effect=OSError("replace failed")):
                with self.assertRaises(OSError):
                    DASHBOARD.atomic_write_text(output, "partial")
            self.assertEqual(output.read_text(encoding="utf-8"), "stable")
            self.assertEqual(output.stat().st_mtime_ns, before_mtime)
            self.assertEqual(list(temporary.glob(".dashboard.html.*.tmp")), [])

    def test_main_reports_nonzero_for_invalid_explorer(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            explorer = temporary / "bad.json"
            output = temporary / "dashboard.html"
            explorer.write_text("{", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                result = DASHBOARD.main(explorer_path=explorer, output_path=output)
            self.assertEqual(result, 1)
            self.assertIn("Dashboard not generated: Explorer file cannot be parsed", stderr.getvalue())

    def test_static_html_and_existing_sections_with_mocked_inputs(self):
        rendered = self.render(explorer_payload())
        for heading in (
            "Dashboard Summary",
            "Portfolio Intelligence",
            "Metric Interpretation",
            "AI Portfolio Commentary",
            "System Health",
            "ETF Watchlist Ranking",
            "AI Risk Monitor",
            "Research Router",
            "Weekly Research Memo",
            "Charts",
        ):
            self.assertIn(heading, rendered)
        self.assertNotIn("<script", rendered.lower())
        self.assertNotIn("fetch(", rendered.lower())
        self.assertNotIn("http://", rendered.lower())
        self.assertNotIn("https://", rendered.lower())


if __name__ == "__main__":
    unittest.main()
