"""Pure deterministic scoring rules shared by the gold research scripts."""


def clamp(x, low=0, high=100):
    return max(low, min(high, x))


def score_correlation(avg_corr):
    return clamp(100 * (1 - avg_corr))


def score_volatility(gld_vol, spy_vol):
    ratio = gld_vol / spy_vol
    if ratio <= 1:
        return 100
    if ratio >= 2:
        return 30
    return clamp(100 - (ratio - 1) * 70)


def score_stress(gld_stress, spy_stress):
    return clamp(50 + (gld_stress - spy_stress) * 2000)


def score_risk_contribution(gld_rc):
    if gld_rc <= 0.25:
        return 90
    if gld_rc <= 0.35:
        return 70
    if gld_rc <= 0.45:
        return 50
    return 30


def calculate_final_score(scores):
    return (
        scores["Correlation Score"] * 0.30
        + scores["Volatility Score"] * 0.25
        + scores["Stress Performance Score"] * 0.25
        + scores["Risk Contribution Score"] * 0.20
    )


def history_score_correlation(avg_corr):
    return max(0, 100 * (1 - avg_corr))


def history_score_volatility(vol_ratio):
    return max(0, min(100, 100 - max(vol_ratio - 1, 0) * 70))


def history_score_stress(stress_gap):
    return max(0, min(100, 50 + stress_gap * 2000))


def calculate_history_component_scores(avg_corr, vol_ratio, stress_gap):
    return (
        history_score_correlation(avg_corr),
        history_score_volatility(vol_ratio),
        history_score_stress(stress_gap),
    )


def calculate_history_gold_score(corr_score, vol_score, stress_score):
    return corr_score * 0.35 + vol_score * 0.30 + stress_score * 0.35
