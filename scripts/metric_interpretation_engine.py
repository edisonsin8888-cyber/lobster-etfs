from pathlib import Path
import pandas as pd


OUTPUT = Path(
    "reports/08_agent_ops/metric_interpretation.txt"
)



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

            return float(
                df.iloc[-1][numeric_cols[0]]
            )

    return None



def read_alert():

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


    return "UNKNOWN"



def read_allocation():

    path = Path(
        "reports/06_score_and_monitor/gold_signal_dashboard.txt"
    )

    if path.exists():

        text = path.read_text()

        for line in text.splitlines():

            if "%" in line:

                return line.split(":")[-1].strip()


    return "UNKNOWN"



def score_interpretation(score):

    if score >= 80:

        return (
            "Strong diversification benefit. "
            "Gold currently provides meaningful portfolio protection."
        )


    elif score >= 60:

        return (
            "Moderate diversification benefit. "
            "Gold contributes positively but requires continued monitoring."
        )


    elif score >= 40:

        return (
            "Mixed diversification effect. "
            "Current benefits are limited by market conditions."
        )


    else:

        return (
            "Limited diversification benefit. "
            "Gold allocation should remain cautious."
        )



def alert_interpretation(alert):

    if alert == "GREEN":

        return (
            "Risk conditions remain stable. "
            "No major warning signals detected."
        )


    elif alert == "YELLOW":

        return (
            "Some risk indicators require monitoring. "
            "Portfolio conditions show early deterioration."
        )


    elif alert == "RED":

        return (
            "Multiple risk indicators indicate elevated stress. "
            "Defensive positioning should be considered."
        )


    return "Risk status unavailable."



def allocation_interpretation(allocation):

    if "0" in allocation:

        return (
            "A conservative allocation range is suggested "
            "because current diversification contribution remains limited."
        )


    elif "5" in allocation:

        return (
            "A moderate allocation range is supported by "
            "improving diversification characteristics."
        )


    return (
        "Allocation recommendation requires further review."
    )



def generate():

    score = read_score()

    alert = read_alert()

    allocation = read_allocation()


    if score is not None:

        score_text = round(score,2)

    else:

        score_text = "N/A"



    report = f"""
Metric Interpretation Report


Gold Diversification Score:

{score_text}

Interpretation:

{score_interpretation(score) if score else "Unavailable"}



Alert Status:

{alert}

Interpretation:

{alert_interpretation(alert)}



Recommended Allocation:

{allocation}

Interpretation:

{allocation_interpretation(allocation)}

"""


    OUTPUT.write_text(
        report,
        encoding="utf-8"
    )


    print(
        "Metric interpretation generated successfully."
    )



if __name__ == "__main__":

    generate()