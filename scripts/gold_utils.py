def score_status(score):
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Moderate"
    if score >= 40:
        return "Mixed"
    return "Weak"


def confidence(score):
    if score >= 70:
        return "High"
    if score >= 55:
        return "Medium"
    return "Low"


def alert_level(avg_corr, vol_ratio, score):
    red_count = sum([avg_corr >= 0.60, vol_ratio >= 1.70, score < 45])
    yellow_count = sum([avg_corr >= 0.30, vol_ratio >= 1.20, score < 70])

    if red_count >= 2:
        return "Red"
    if red_count == 1 or yellow_count >= 2:
        return "Yellow"
    return "Green"


def allocation_score(score, stress_gap, avg_corr, vol_ratio):
    out = 50
    out += 15 if stress_gap > 0 else 0
    out += 10 if avg_corr < 0.45 else -10 if avg_corr > 0.65 else 0
    out += 10 if vol_ratio < 1.50 else -10 if vol_ratio > 1.80 else 0
    out += 10 if score >= 60 else -10 if score < 45 else 0
    return max(0, min(100, out))


def strategic_range(score, avg_corr, vol_ratio, stress_gap):
    if stress_gap > 0 and score >= 55 and avg_corr < 0.60 and vol_ratio < 1.80:
        return "5%–15%"
    if stress_gap > 0 and score >= 45 and avg_corr < 0.70:
        return "5%–10%"
    return "0%–5%"


def best_step(score, stress_gap, vol_ratio):
    if score < 45 or vol_ratio > 2.0:
        return "0% to 5%"
    if stress_gap > 0 and score >= 55:
        return "5% to 10%"
    return "0% to 5%"


def direction(change, threshold=2):
    if change > threshold:
        return "Improving"
    if change < -threshold:
        return "Deteriorating"
    return "Stable"


def range_transition(prev, curr):
    order = {"0%–5%": 0, "5%–10%": 1, "5%–15%": 2}
    diff = order[curr] - order[prev]

    if diff > 0:
        return "Loosened"
    if diff < 0:
        return "Tightened"
    return "Unchanged"


def alert_transition(prev, curr):
    order = {"Green": 0, "Yellow": 1, "Red": 2}
    diff = order[curr] - order[prev]

    if diff > 0:
        return "Deteriorated"
    if diff < 0:
        return "Improved"
    return "Unchanged"

def allocation_stance(allocation_score):
    if allocation_score >= 70:
        return "Supportive"
    if allocation_score >= 55:
        return "Cautious"
    return "Defensive"