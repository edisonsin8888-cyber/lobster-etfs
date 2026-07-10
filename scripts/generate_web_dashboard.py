from pathlib import Path
from datetime import datetime
import pandas as pd
import re

DOC_PATH = Path(
    "docs/dashboard.html"
)


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

def generate_dashboard():


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


    DOC_PATH.write_text(
        html,
        encoding="utf-8"
    )


    print(
        "Dashboard generated successfully."
    )



if __name__ == "__main__":

    generate_dashboard()