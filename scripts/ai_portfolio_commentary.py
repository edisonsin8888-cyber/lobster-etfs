from pathlib import Path
from datetime import datetime


OUTPUT = Path(
    "reports/08_agent_ops/ai_portfolio_commentary.txt"
)



def read_file(path):

    if path.exists():

        return path.read_text()

    return ""



def generate_commentary():


    gold = read_file(
        Path(
            "reports/06_score_and_monitor/gold_signal_dashboard.txt"
        )
    )


    risk = read_file(
        Path(
            "reports/06_score_and_monitor/ai_risk_monitor_report.txt"
        )
    )


    router = read_file(
        Path(
            "reports/07_lobster_watchlist/lobster_research_router.txt"
        )
    )


    commentary = f"""
AI Portfolio Commentary

Generated Time:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


Portfolio Overview:

The system currently evaluates ETF allocation opportunities
through diversification analysis, risk monitoring, and research routing.


Gold Defensive Sleeve:

{gold}


Risk Assessment:

{risk}


Research Priority:

{router}


Investment Interpretation:

The portfolio maintains a risk-aware allocation framework.
Gold is monitored as a defensive diversification component,
while equity growth exposure requires continuous evaluation
under changing market conditions.

The research engine prioritizes assets with significant
risk-return characteristics for further investigation.
"""


    OUTPUT.write_text(
        commentary,
        encoding="utf-8"
    )


    print(
        "AI Portfolio Commentary generated successfully."
    )



if __name__ == "__main__":

    generate_commentary()