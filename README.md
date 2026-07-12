# Lobster ETF Research Assistant v2

A Python-based multi-sleeve ETF research assistant that combines ETF watchlist scanning, ETF scoring, research routing, a completed GLD defensive diversification engine, and an XLK growth-sleeve monitor.

This project is designed as a simplified asset-management research workflow. It does not aim to predict short-term ETF prices. Instead, it asks:

> Which ETFs currently deserve deeper research attention, what portfolio role do they play, and how should defensive and growth ETF sleeves be evaluated?

---

## 1. Project Objective

The goal of this project is to build a repeatable ETF research pipeline that can:

1. scan a core ETF universe,
2. classify each ETF into a portfolio sleeve,
3. generate a comparable ETF attractiveness score,
4. route the next deep-dive research candidate,
5. evaluate GLD as a defensive diversification sleeve,
6. evaluate XLK as a growth / sector sleeve,
7. generate dashboards, chart packs, router outputs, and weekly research memos automatically.

The system can be refreshed through one command:

```bash
python scripts/run_all.py
```

### Research Copilot

The terminal Research Copilot answers questions only from the generated AI research packet. Set `OPENAI_API_KEY` in your environment; never place the key in Git, source files, reports, or `.env` files that may be committed.

Validate the request setup without an API call:

```bash
.venv/bin/python scripts/research_copilot.py --dry-run "当前 GLD 分散化状态是什么？"
```

Run a research query:

```bash
OPENAI_API_KEY="your-key" .venv/bin/python scripts/research_copilot.py "当前 GLD 分散化状态是什么？"
```

Export a no-cost, copy-ready prompt for ChatGPT or VS Code Codex (no API key or API call is required):

```bash
.venv/bin/python scripts/research_copilot.py --export-prompt "为什么当前黄金配置建议维持在这个区间？"
```

Copy the exported prompt from the terminal, or from `reports/07_ai_research/latest_copilot_prompt.md`, into ChatGPT or VS Code Codex. The generated prompt can contain market-research data, so review it before sharing it with any external service.

---

## 2. ETF Universe

The current ETF universe includes five ETFs:

- **SPY** — Core U.S. equity sleeve
- **QQQ** — Growth / technology-heavy equity sleeve
- **GLD** — Defensive diversification sleeve
- **TLT** — Rate-sensitive defensive sleeve
- **XLK** — Tactical technology sector sleeve

This universe gives the system exposure to broad equity beta, growth exposure, defensive assets, duration sensitivity, and sector concentration.

---

## 3. System Architecture

Lobster v2 is organized into five layers:

1. ETF Watchlist Scanner
2. ETF Score Engine
3. Research Router v2
4. Deep-Dive Sleeve Modules
5. Dashboard and Weekly Memo Layer

Together, these layers create a research workflow:

```text
ETF Watchlist
→ ETF Score Engine
→ Research Router v2
→ GLD Defensive Engine / XLK Growth Monitor
→ Dashboard and Weekly Memo
```

---

## 4. Layer 1 — ETF Watchlist Scanner

The first layer of the Lobster ETF Research Assistant is the ETF Watchlist Scanner.

This layer provides a top-level view of the ETF universe before deeper analysis is conducted. It scans a small group of core ETFs and identifies their recent performance, risk condition, portfolio role, and research priority.

The scanner calculates the following indicators for each ETF:

- 1-month return
- 3-month return
- annualized volatility
- 3-month maximum drawdown
- momentum flag
- risk flag
- portfolio role tag
- research priority
- short ETF-level interpretation

The purpose of this layer is not to make final allocation decisions. Instead, it acts as the first screening layer of the system. It helps answer:

> Which ETFs are currently showing strong performance, weak performance, high volatility, or unusual risk conditions?

Current watchlist result:

- **Best 3M performer:** XLK
- **Weakest 3M performer:** GLD
- **Highest-volatility ETF:** XLK
- **Highest research-priority ETF:** GLD

This layer is important because it prevents the project from being only a single-asset GLD study. GLD is placed inside a broader ETF research universe, and the system first scans multiple ETF sleeves before deciding which ETF deserves deeper research attention.

Main script:

```text
scripts/etf_watchlist_monitor.py
```

Main output files:

```text
reports/07_lobster_watchlist/etf_watchlist_snapshot.csv
reports/07_lobster_watchlist/etf_watchlist_summary.txt
```

---

## 5. Layer 2 — ETF Score Engine

The second layer is the ETF Score Engine.

This layer converts watchlist signals into a comparable ETF attractiveness score. Instead of only labeling ETFs with role tags, the system assigns each ETF a numerical score so that SPY, QQQ, GLD, TLT, and XLK can be compared under one framework.

The ETF Score Engine calculates:

- Momentum Score
- Risk Score
- Drawdown Score
- Role Score
- Final ETF Score
- ETF Stance

The scoring logic is designed to combine both performance and portfolio role. For example, an ETF with strong momentum but very high volatility may receive a constructive score, but it can still be flagged as high risk. This makes the score more useful than a simple return ranking.

The ETF stance is classified as:

- **Constructive**
- **Neutral**
- **Defensive**

This layer helps answer:

> Which ETFs look attractive after considering momentum, volatility, drawdown, and portfolio role together?

Main script:

```text
scripts/etf_score_engine.py
```

Main output files:

```text
reports/07_lobster_watchlist/etf_score_table.csv
reports/07_lobster_watchlist/etf_score_summary.txt
```

---

## 6. Layer 3 — Research Router v2

The third layer is the Research Router v2.

The router decides which ETF deserves deeper research attention next. It does not simply rank ETFs by return. Instead, it combines multiple signals from the watchlist and score engine.

Router v2 considers:

- ETF attractiveness score
- watchlist research priority
- portfolio role
- momentum condition
- risk condition
- recent deterioration
- deep-dive module availability

The router gives each ETF a Router v2 Score and produces a ranked research queue.

Current router result:

- **Next deep-dive candidate:** GLD
- **Reason:** high watchlist priority, weak momentum, elevated risk, negative 3-month return, and completed Gold Engine availability

This layer is important because it gives the project a research workflow:

```text
scan → score → prioritize → deep-dive → summarize
```

Main script:

```text
scripts/lobster_research_router.py
```

Main output file:

```text
reports/07_lobster_watchlist/lobster_research_router.txt
```

---

## 7. Layer 4 — Deep-Dive Sleeve Modules

The fourth layer contains the deep-dive ETF sleeve modules.

Lobster v2 currently has two sleeve modules:

1. GLD Defensive Diversification Engine
2. XLK Growth Sleeve Monitor

These modules allow the system to move beyond broad ETF screening and into deeper portfolio interpretation.

---

### 7.1 GLD Defensive Diversification Engine

The GLD module is the most developed deep-dive module in the current project.

It evaluates whether GLD currently improves portfolio diversification and what allocation range is justified.

The Gold Engine analyzes:

- rolling GLD-equity correlation
- GLD / SPY rolling volatility ratio
- stress-period return gap
- GLD portfolio risk contribution
- risk-budget sensitivity across different GLD weights
- marginal allocation efficiency
- recommended strategic allocation range

The core question is:

> Does GLD currently improve portfolio construction, and how much GLD is justified?

Current GLD output:

- **Gold Diversification Score:** 53.89 / 100
- **Score Status:** Mixed
- **Alert Level:** Red
- **Allocation Guidance Score:** 40.00 / 100
- **Allocation Stance:** Defensive
- **Recommended Strategic Range:** 0%–5%

Interpretation:

GLD still has some diversification value, but the current allocation case is weak. The system therefore supports only a small strategic allocation range of **0%–5%**. In the current system, GLD is better treated as a conditional defensive hedge sleeve rather than a large strategic allocation.

Main scripts:

```text
scripts/gold_diversification_score.py
scripts/diversification_alert.py
scripts/ai_risk_monitor.py
scripts/allocation_history_tracker.py
scripts/gold_signal_dashboard.py
scripts/gold_dashboard_charts.py
scripts/gold_dashboard_pack.py
```

Main output files:

```text
reports/06_score_and_monitor/gold_diversification_score.csv
reports/06_score_and_monitor/diversification_alert.txt
reports/06_score_and_monitor/ai_risk_monitor_report.txt
reports/06_score_and_monitor/allocation_history.csv
reports/06_score_and_monitor/allocation_history_summary.txt
reports/06_score_and_monitor/gold_signal_dashboard.txt
reports/06_score_and_monitor/gold_dashboard_pack.md
reports/06_score_and_monitor/gold_div_score_history.png
reports/06_score_and_monitor/allocation_guidance_history.png
reports/06_score_and_monitor/gld_risk_budget_curve.png
reports/weekly_reports/gold_weekly_memo.txt
```

---

### 7.2 XLK Growth Sleeve Monitor

The XLK module is the first growth / sector sleeve monitor in Lobster v2.

It evaluates whether XLK is showing genuine growth leadership relative to SPY or only a high-volatility rebound.

The XLK Growth Monitor analyzes:

- XLK vs SPY 1-month return
- XLK vs SPY 3-month return
- XLK 3-month excess return
- XLK volatility premium
- XLK drawdown relative to SPY
- risk-adjusted growth view
- growth-sleeve score
- growth-sleeve risk flag
- tactical growth stance

The core question is:

> Is XLK currently a constructive growth sleeve, or is its outperformance mainly driven by high-risk rebound behavior?

Current XLK output:

- **XLK 3M Return:** 32.80%
- **SPY 3M Return:** 13.86%
- **XLK 3M Excess Return:** 18.94%
- **XLK Annualized Volatility:** 31.90%
- **SPY Annualized Volatility:** 13.71%
- **Growth Sleeve Score:** 70.40 / 100
- **Growth Sleeve Risk Flag:** High Growth Risk
- **Tactical Growth Stance:** Constructive Growth Sleeve

Interpretation:

XLK shows strong growth leadership relative to SPY, but this comes with elevated volatility and drawdown risk. The system therefore treats XLK as a constructive but high-risk growth / sector sleeve.

Main script:

```text
scripts/xlk_growth_monitor.py
```

Main output files:

```text
reports/08_growth_sleeve/xlk_vs_spy_summary.csv
reports/08_growth_sleeve/xlk_growth_monitor.txt
```

---

## 8. Layer 5 — Dashboard and Weekly Memo Layer

The fifth layer is the reporting layer.

This layer converts quantitative outputs into readable investment research summaries. It allows the project to communicate results in a format closer to an asset-management research workflow.

The reporting layer generates:

- Gold signal dashboard
- Gold dashboard pack
- dashboard charts
- Lobster dashboard
- Lobster weekly research memo

The Lobster Dashboard v2 combines:

- ETF Watchlist
- ETF Score Engine
- Research Router v2
- Gold Engine
- XLK Growth Monitor

The Lobster Weekly Memo v2 summarizes:

1. Weekly Research Focus
2. ETF Market Snapshot
3. ETF Score Ranking
4. Defensive Sleeve Update: GLD
5. Growth Sleeve Update: XLK
6. Router v2 Decision
7. Weekly Research Conclusion
8. Next Action

Main scripts:

```text
scripts/lobster_dashboard.py
scripts/lobster_weekly_memo.py
```

Main output files:

```text
reports/07_lobster_watchlist/lobster_dashboard.txt
reports/07_lobster_watchlist/lobster_weekly_memo.txt
```

Additional reporting outputs:

```text
reports/06_score_and_monitor/gold_signal_dashboard.txt
reports/06_score_and_monitor/gold_dashboard_pack.md
reports/06_score_and_monitor/gold_div_score_history.png
reports/06_score_and_monitor/allocation_guidance_history.png
reports/06_score_and_monitor/gld_risk_budget_curve.png
```

---

## 9. How to Run the Full Pipeline

Run the following command from the project root:

```bash
python scripts/run_all.py
```

This refreshes the full system:

1. Gold Diversification Score
2. Diversification Alert
3. AI Risk Monitor
4. Allocation History Tracker
5. Gold Signal Dashboard
6. Gold Dashboard Charts
7. Gold Dashboard Pack
8. ETF Watchlist Monitor
9. ETF Score Engine
10. Lobster Dashboard
11. Lobster Research Router v2
12. XLK Growth Monitor
13. Lobster Weekly Memo v2

If the pipeline runs successfully, the terminal should show:

```text
All core reports refreshed successfully.
```

---

## 10. Project Structure

```text
lobster-etfs/
│
├─ data/
│  ├─ spy.csv
│  ├─ qqq.csv
│  ├─ gld.csv
│  ├─ tlt.csv
│  └─ xlk.csv
│
├─ reports/
│  ├─ 02_regime_analysis/
│  ├─ 05_weight_sensitivity/
│  ├─ 06_score_and_monitor/
│  ├─ 07_lobster_watchlist/
│  ├─ 08_growth_sleeve/
│  └─ weekly_reports/
│
├─ scripts/
│  ├─ gold_utils.py
│  ├─ gold_diversification_score.py
│  ├─ diversification_alert.py
│  ├─ ai_risk_monitor.py
│  ├─ allocation_history_tracker.py
│  ├─ gold_signal_dashboard.py
│  ├─ gold_dashboard_charts.py
│  ├─ gold_dashboard_pack.py
│  ├─ etf_watchlist_monitor.py
│  ├─ etf_score_engine.py
│  ├─ lobster_research_router.py
│  ├─ lobster_dashboard.py
│  ├─ lobster_weekly_memo.py
│  ├─ xlk_growth_monitor.py
│  └─ run_all.py
│
├─ README.md
└─ PROJECT_BRIEF.md
```

---

## 11. Core Scripts

### Gold Engine

```text
scripts/gold_diversification_score.py
scripts/diversification_alert.py
scripts/ai_risk_monitor.py
scripts/allocation_history_tracker.py
scripts/gold_signal_dashboard.py
scripts/gold_dashboard_charts.py
scripts/gold_dashboard_pack.py
```

### Lobster System Layer

```text
scripts/etf_watchlist_monitor.py
scripts/etf_score_engine.py
scripts/lobster_research_router.py
scripts/lobster_dashboard.py
scripts/lobster_weekly_memo.py
```

### Growth Sleeve Layer

```text
scripts/xlk_growth_monitor.py
```

### Pipeline Controller

```text
scripts/run_all.py
```

### Shared Utilities

```text
scripts/gold_utils.py
```

---

## 12. What This Project Demonstrates

This project demonstrates how a financial research question can be developed into a repeatable investment research workflow.

### Finance and portfolio research skills

- ETF sleeve classification
- diversification analysis
- defensive asset evaluation
- growth-sleeve monitoring
- rolling correlation and volatility analysis
- stress-period performance analysis
- risk-budget sensitivity
- allocation guidance logic
- ETF score interpretation
- research-priority routing

### Technical skills

- Python scripting
- modular pipeline design
- automated report generation
- CSV output handling
- text report generation
- dashboard construction
- chart generation
- one-command pipeline execution

### Research communication skills

- translating quantitative outputs into investment interpretation
- writing dashboard-style summaries
- creating weekly memo-style research reports
- explaining limitations and next research direction

---

## 13. Current Bottom Line

Lobster v2 identifies a two-sleeve research structure:

- **GLD** remains the completed defensive diversification deep-dive module.
- **XLK** becomes the first growth / sector sleeve monitor.

The current portfolio research stance is mixed.

GLD is useful for defensive monitoring, but the Gold Engine does not support aggressive allocation under current conditions. The recommended strategic range remains **0%–5%**.

XLK shows strong growth leadership relative to SPY, but this comes with high volatility risk. The system therefore treats XLK as a constructive but high-risk growth sleeve.

The project demonstrates how a single financial research question about gold ETF diversification can be expanded into a broader ETF research assistant with scanning, scoring, routing, deep-dive analysis, and automated reporting.

---

## 14. Limitations

The current version is a working research prototype, but several limitations remain.

### 1. Small ETF universe

The system currently tracks five ETFs. Future versions could include more sector ETFs, factor ETFs, commodity ETFs, bond ETFs, and international equity ETFs.

### 2. Rule-based scoring

The ETF Score Engine and Research Router v2 use transparent rule-based logic. This improves interpretability, but the scoring framework is still simplified.

### 3. Limited number of deep-dive modules

GLD has a completed deep-dive engine, and XLK has a light growth-sleeve monitor. Other ETFs such as TLT, QQQ, and SPY are not yet developed into full sleeve modules.

### 4. Historical-data dependence

The results depend on the historical sample, rolling windows, and chosen thresholds. Different time windows may produce different allocation signals.

### 5. No live automation yet

The current system can be refreshed manually through `run_all.py`, but it does not yet run on a scheduled automatic basis.

---

## 15. Future Extensions

Potential next steps include:

1. building a TLT rate-sensitive defensive module,
2. building a QQQ growth comparison module,
3. expanding the ETF universe,
4. refining the ETF Score Engine,
5. adding regime-aware scoring,
6. adding downside-risk measures,
7. creating a visual HTML dashboard,
8. automating weekly data updates,
9. connecting the system to live market data,
10. expanding from sleeve-level analysis to a broader ETF allocation engine.

---

## 16. Final Project Description

Lobster ETF Research Assistant v2 is a Python-based multi-sleeve ETF research system.

It scans a core ETF universe, assigns ETF attractiveness scores, routes research priorities, and combines a completed GLD defensive diversification engine with an XLK growth-sleeve monitor.

The system does not try to provide direct trading signals. Instead, it focuses on portfolio research questions:

- What role does each ETF play?
- Which ETF currently deserves deeper research?
- Does GLD still work as a defensive diversification sleeve?
- Is XLK showing constructive growth leadership or high-risk rebound behavior?
- How can quantitative indicators be translated into readable investment research?

By combining portfolio logic, Python automation, and research communication, the project turns a single ETF case study into a repeatable asset-management research workflow.
