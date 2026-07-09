# Project Brief  
## Lobster ETF Research Assistant v2  
### ETF Score Engine + Research Router v2 + GLD Defensive Engine + XLK Growth Monitor

---

## 1. Project Overview

**Lobster ETF Research Assistant v2** is a Python-based multi-sleeve ETF research system.

The project started from a focused question about whether **GLD**, a gold ETF, still provides diversification value in a multi-asset portfolio. After completing the GLD deep-dive module, the project was expanded into a broader ETF research assistant.

The current system can:

1. scan a core ETF universe,
2. classify ETFs by portfolio role,
3. generate ETF attractiveness scores,
4. route research priorities,
5. evaluate GLD as a defensive diversification sleeve,
6. evaluate XLK as a growth / sector sleeve,
7. generate dashboards and weekly research memos automatically.

The system can be refreshed through one command:

```bash
python scripts/run_all.py
```

This makes the project a small but repeatable investment research workflow.

---

## 2. Project Question

The main research question is:

> **How can a Python-based ETF research assistant identify which ETFs deserve deeper research attention, classify their portfolio roles, and evaluate defensive and growth ETF sleeves using quantitative indicators?**

The project does not aim to predict short-term ETF prices. Instead, it focuses on a more asset-management-oriented question:

> **What role does each ETF play in a portfolio, and which ETF currently deserves deeper research based on risk, return, drawdown, and portfolio function?**

This makes the project closer to a simplified portfolio research process rather than a simple price-tracking tool.

---

## 3. Project Motivation

I am interested in asset management, portfolio construction, and quantitative investment research.

In portfolio management, the important question is often not simply whether an asset will rise or fall. A more meaningful question is whether the asset improves the structure, risk balance, or diversification quality of a portfolio.

This project was built around that idea.

Gold was chosen as the first deep-dive module because GLD is often described as a defensive or diversification asset. However, this role should not be assumed automatically. It should be tested using data such as:

- rolling correlation with equity ETFs,
- relative volatility compared with SPY,
- stress-period performance,
- portfolio risk contribution,
- allocation sensitivity under different GLD weights.

After completing the Gold Engine, I expanded the system into a broader ETF research assistant by adding:

- ETF watchlist monitoring,
- ETF score engine,
- ETF research router,
- XLK growth-sleeve monitor,
- Lobster dashboard,
- weekly research memo.

This upgraded the project from a single-ETF case study into a small multi-sleeve ETF research framework.

---

## 4. ETF Universe

The current version tracks five ETFs:

- **SPY** — Core U.S. equity sleeve
- **QQQ** — Growth / technology-heavy equity sleeve
- **GLD** — Defensive diversification sleeve
- **TLT** — Rate-sensitive defensive sleeve
- **XLK** — Tactical technology sector sleeve

This universe is intentionally small. It allows the system to remain understandable and maintainable while still covering several important portfolio roles:

- broad equity beta,
- growth exposure,
- defensive assets,
- interest-rate sensitivity,
- sector concentration.

---

## 5. System Architecture

Lobster v2 is organized into five layers:

1. ETF Watchlist Scanner
2. ETF Score Engine
3. Research Router v2
4. Deep-Dive Sleeve Modules
5. Dashboard and Weekly Memo Layer

The workflow is:

```text
ETF Watchlist Scanner
→ ETF Score Engine
→ Research Router v2
→ GLD Defensive Engine / XLK Growth Monitor
→ Dashboard and Weekly Memo
```

This structure makes the project more systematic than a normal ETF table. It moves from market observation to scoring, routing, deep-dive analysis, and final research communication.

---

## 6. Layer 1 — ETF Watchlist Scanner

The first layer is the ETF Watchlist Scanner.

This layer gives the system a top-level view of the ETF universe. It calculates basic performance and risk indicators for each ETF.

The scanner calculates:

- 1-month return,
- 3-month return,
- annualized volatility,
- 3-month maximum drawdown,
- momentum flag,
- risk flag,
- portfolio role tag,
- research priority,
- short ETF-level interpretation.

The purpose of this layer is not to make final allocation decisions. It acts as the first screening layer.

It helps answer:

> **Which ETFs are currently showing strong performance, weak performance, high volatility, or unusual risk conditions?**

Current watchlist result:

- **Best 3M performer:** XLK
- **Weakest 3M performer:** GLD
- **Highest-volatility ETF:** XLK
- **Highest research-priority ETF:** GLD

Main script:

```text
scripts/etf_watchlist_monitor.py
```

Main output files:

```text
reports/07_lobster_watchlist/etf_watchlist_snapshot.csv
reports/07_lobster_watchlist/etf_watchlist_summary.txt
```

This layer is important because it places GLD inside a broader ETF universe. GLD is not analyzed in isolation; it is first compared with other ETF sleeves.

---

## 7. Layer 2 — ETF Score Engine

The second layer is the ETF Score Engine.

The ETF Score Engine converts watchlist signals into a comparable ETF attractiveness score. This allows SPY, QQQ, GLD, TLT, and XLK to be compared under one framework.

It calculates:

- Momentum Score,
- Risk Score,
- Drawdown Score,
- Role Score,
- Final ETF Score,
- ETF Stance.

The ETF Stance is classified as:

- **Constructive**
- **Neutral**
- **Defensive**

This layer helps answer:

> **Which ETFs look attractive after considering momentum, volatility, drawdown, and portfolio role together?**

The score is not a direct buy or sell signal. It is a research prioritization tool. It helps the system decide which ETF deserves closer attention.

Main script:

```text
scripts/etf_score_engine.py
```

Main output files:

```text
reports/07_lobster_watchlist/etf_score_table.csv
reports/07_lobster_watchlist/etf_score_summary.txt
```

This is one of the key v2 upgrades because it turns the watchlist from a descriptive table into a scoring system.

---

## 8. Layer 3 — Research Router v2

The third layer is the Research Router v2.

The router decides which ETF deserves deeper research attention next. It does not rank ETFs only by recent returns. Instead, it combines several signals.

Router v2 considers:

- ETF attractiveness score,
- watchlist research priority,
- portfolio role,
- momentum condition,
- risk condition,
- recent deterioration,
- deep-dive module availability.

It produces:

- a next deep-dive candidate,
- a ranked research queue,
- a router reason,
- a Router v2 Score.

Current router result:

- **Next deep-dive candidate:** GLD
- **Reason:** high watchlist priority, weak momentum, elevated risk, negative 3-month return, and completed Gold Engine availability.

Main script:

```text
scripts/lobster_research_router.py
```

Main output file:

```text
reports/07_lobster_watchlist/lobster_research_router.txt
```

This layer gives the project a research workflow:

```text
scan → score → prioritize → deep-dive → summarize
```

It makes the system more than a passive dashboard.

---

## 9. Layer 4 — Deep-Dive Sleeve Modules

The fourth layer contains the deep-dive ETF sleeve modules.

Lobster v2 currently has two sleeve modules:

1. GLD Defensive Diversification Engine
2. XLK Growth Sleeve Monitor

These modules allow the system to move beyond broad ETF screening and into deeper portfolio interpretation.

---

## 10. GLD Defensive Diversification Engine

The GLD module is the most complete deep-dive module in the current project.

It evaluates whether GLD currently improves portfolio diversification and what allocation range is justified.

The Gold Engine analyzes:

- rolling GLD-equity correlation,
- GLD / SPY rolling volatility ratio,
- stress-period return gap,
- GLD portfolio risk contribution,
- risk-budget sensitivity across different GLD weights,
- marginal allocation efficiency,
- recommended strategic allocation range.

The key research question is:

> **Does GLD currently improve portfolio construction, and how much GLD is justified?**

Current GLD result:

- **Gold Diversification Score:** 53.89 / 100
- **Score Status:** Mixed
- **Alert Level:** Red
- **Allocation Guidance Score:** 40.00 / 100
- **Allocation Stance:** Defensive
- **Recommended Strategic Range:** 0%–5%

Interpretation:

GLD still has some diversification value, but the current allocation case is weak. The system therefore supports only a small strategic allocation range of **0%–5%**.

This means GLD is currently treated as a conditional defensive hedge sleeve, not as a large strategic allocation.

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

## 11. XLK Growth Sleeve Monitor

The XLK module is the first growth / sector sleeve monitor in Lobster v2.

It evaluates whether XLK is showing genuine growth leadership relative to SPY or only a high-volatility rebound.

The XLK Growth Monitor analyzes:

- XLK vs SPY 1-month return,
- XLK vs SPY 3-month return,
- XLK 3-month excess return,
- XLK volatility premium,
- XLK drawdown relative to SPY,
- risk-adjusted growth view,
- growth-sleeve score,
- growth-sleeve risk flag,
- tactical growth stance.

The key research question is:

> **Is XLK currently a constructive growth sleeve, or is its outperformance mainly driven by high-risk rebound behavior?**

Current XLK result:

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

## 12. Layer 5 — Dashboard and Weekly Memo Layer

The fifth layer is the reporting layer.

This layer converts quantitative outputs into readable investment research summaries. It helps communicate the results in a format closer to an asset-management research workflow.

The reporting layer includes:

- Gold Signal Dashboard,
- Gold Dashboard Pack,
- dashboard charts,
- Lobster Dashboard,
- Lobster Weekly Research Memo.

The Lobster Dashboard v2 combines:

- ETF Watchlist,
- ETF Score Engine,
- Research Router v2,
- Gold Engine,
- XLK Growth Monitor.

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

## 13. How the Full Pipeline Runs

The whole system can be refreshed by running:

```bash
python scripts/run_all.py
```

This command runs the main modules in sequence:

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

If the pipeline runs successfully, the terminal shows:

```text
All core reports refreshed successfully.
```

This one-command execution is important because it makes the project repeatable rather than manually assembled.

---

## 14. What v2 Improved Compared with v1

The v1 system already had:

- Gold Engine,
- ETF Watchlist Monitor,
- Lobster Dashboard,
- Research Router,
- Weekly Memo.

However, v1 had one main limitation:

> The Gold Engine was strong, but the other ETFs were mostly only described at the watchlist level.

v2 improves this by adding:

1. **ETF Score Engine**  
   ETFs are now compared through a unified scoring framework.

2. **Research Router v2**  
   Router decisions now use ETF score, risk condition, portfolio role, momentum, deterioration, and deep-dive availability.

3. **XLK Growth Sleeve Monitor**  
   The system now has a second sleeve module beyond GLD.

4. **Dashboard v2 and Weekly Memo v2**  
   Reporting now integrates ETF score ranking, GLD defensive analysis, XLK growth analysis, and router decision.

As a result, the project has moved from a gold-focused ETF assistant to a multi-sleeve ETF research assistant.

---

## 15. Current Research Interpretation

The current system identifies a two-sleeve research structure:

```text
GLD = Defensive Diversification Sleeve
XLK = Growth / Sector Sleeve
```

### GLD Interpretation

GLD remains important because it is the completed defensive deep-dive module. However, the Gold Engine remains cautious. The current allocation stance is defensive, and the recommended strategic range is only **0%–5%**.

This suggests that GLD should remain under monitoring, but the system does not support aggressive allocation under current conditions.

### XLK Interpretation

XLK shows strong growth leadership relative to SPY. Its 3-month excess return is positive, and the Growth Sleeve Score is constructive.

However, XLK also has much higher volatility than SPY. This means its growth signal is attractive, but risk control is necessary.

### Overall Portfolio Research Stance

The overall research stance is mixed:

- GLD provides defensive monitoring value but weak allocation support.
- XLK provides growth leadership but high volatility risk.
- The router keeps GLD as the active deep-dive candidate because a completed Gold Engine is available and GLD has high research priority.
- XLK is the key growth-sleeve monitor and may become a future deep-dive module.

---

## 16. Skills Demonstrated

This project demonstrates a combination of finance knowledge, quantitative thinking, technical execution, and research communication.

### Finance and investment research skills

- ETF sleeve classification
- diversification analysis
- defensive asset evaluation
- growth-sleeve monitoring
- rolling correlation analysis
- volatility comparison
- drawdown analysis
- stress-period performance analysis
- risk-budget sensitivity
- allocation guidance logic
- ETF score interpretation
- research-priority routing

### Technical skills

- Python scripting
- modular pipeline design
- pandas data analysis
- CSV output handling
- text report generation
- chart generation
- dashboard construction
- one-command pipeline execution
- project file organization

### Research communication skills

- translating quantitative outputs into investment interpretation
- writing dashboard-style summaries
- creating weekly memo-style research reports
- explaining current findings
- identifying limitations and future extensions

---

## 17. Project Limitations

The current version is a working research prototype, but several limitations remain.

### 1. Small ETF universe

The system currently tracks five ETFs. Future versions could include more sector ETFs, factor ETFs, commodity ETFs, bond ETFs, and international equity ETFs.

### 2. Rule-based scoring

The ETF Score Engine and Research Router v2 use transparent rule-based logic. This improves interpretability, but the scoring framework is still simplified.

### 3. Limited number of deep-dive modules

GLD has a completed deep-dive engine, and XLK has a light growth-sleeve monitor. Other ETFs such as TLT, QQQ, and SPY are not yet developed into full sleeve modules.

### 4. Historical-data dependence

The results depend on the historical sample, rolling windows, and chosen thresholds. Different time windows may produce different allocation signals.

### 5. No scheduled automation yet

The system can be refreshed manually through `run_all.py`, but it does not yet run on a scheduled automatic basis.

These limitations are useful because they define clear directions for future development.

---

## 18. Future Extensions

The next possible extensions include:

1. building a TLT rate-sensitive defensive module,
2. building a QQQ growth comparison module,
3. expanding the ETF universe,
4. refining the ETF Score Engine,
5. adding regime-aware scoring,
6. adding downside-risk measures,
7. adding portfolio-level allocation simulation,
8. creating a visual HTML dashboard,
9. automating weekly data updates,
10. connecting the system to live market data.

The most realistic next step would be to build a **TLT rate-sensitive defensive module** or a **QQQ growth comparison module**, because both would naturally extend the current GLD + XLK two-sleeve structure.

---

## 19. Why This Project Is Valuable

This project is valuable because it shows how a financial research question can be converted into a working technical system.

It is not only a written report about ETFs. It is a repeatable pipeline that can refresh data, calculate indicators, generate scores, route research attention, and produce readable investment summaries.

The project combines:

- portfolio theory,
- ETF research,
- risk analysis,
- Python automation,
- dashboard reporting,
- investment interpretation.

It also demonstrates a realistic research mindset. Instead of assuming that gold is always a hedge or that technology ETFs are always attractive, the system evaluates those claims using indicators and structured logic.

---

## 20. Final Project Description

**Lobster ETF Research Assistant v2** is a Python-based multi-sleeve ETF research system.

It scans a core ETF universe, assigns ETF attractiveness scores, routes research priorities, and combines a completed GLD defensive diversification engine with an XLK growth-sleeve monitor.

The system does not provide direct trading signals. Instead, it focuses on portfolio research questions:

- What role does each ETF play?
- Which ETF currently deserves deeper research?
- Does GLD still work as a defensive diversification sleeve?
- Is XLK showing constructive growth leadership or high-risk rebound behavior?
- How can quantitative indicators be translated into readable investment research?

By combining portfolio logic, Python automation, and research communication, the project turns a single gold ETF case study into a broader ETF research assistant.