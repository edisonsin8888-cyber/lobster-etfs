import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path("reports/06_score_and_monitor")
WEIGHT_DIR = Path("reports/05_weight_sensitivity")

HISTORY_FILE = BASE / "allocation_history.csv"
RISK_BUDGET_FILE = WEIGHT_DIR / "gld_risk_budget_sensitivity.csv"

OUT_SCORE = BASE / "gold_div_score_history.png"
OUT_ALLOC = BASE / "allocation_guidance_history.png"
OUT_RISK = BASE / "gld_risk_budget_curve.png"


def save_line_chart(df, x, y, title, ylabel, output, thresholds=None):
    plt.figure(figsize=(10, 6))
    plt.plot(df[x], df[y], marker="o")

    if thresholds:
        for level in thresholds:
            plt.axhline(level, linestyle="--", linewidth=1)

    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output, dpi=300)
    plt.close()


history = pd.read_csv(HISTORY_FILE)
history["Date"] = pd.to_datetime(history["Date"])

risk_budget = pd.read_csv(RISK_BUDGET_FILE)

save_line_chart(
    history,
    "Date",
    "Gold Diversification Score",
    "Gold Diversification Score History",
    "Score",
    OUT_SCORE,
    thresholds=[40, 60, 80],
)

save_line_chart(
    history,
    "Date",
    "Allocation Guidance Score",
    "Allocation Guidance Score History",
    "Score",
    OUT_ALLOC,
    thresholds=[55, 70],
)

plt.figure(figsize=(10, 6))
plt.plot(
    risk_budget["GLD Weight"],
    risk_budget["GLD Risk Contribution"],
    marker="o",
)
plt.title("GLD Risk Contribution Across Allocation Weights")
plt.xlabel("GLD Weight")
plt.ylabel("GLD Risk Contribution")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUT_RISK, dpi=300)
plt.close()

print("Saved charts:")
print(OUT_SCORE)
print(OUT_ALLOC)
print(OUT_RISK)