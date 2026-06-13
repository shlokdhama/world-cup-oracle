import math
from html import escape


def flag_for(country: str) -> str:
    overrides = {
        "England": "🏴",
        "Scotland": "🏴",
        "Wales": "🏴",
        "Northern Ireland": "🏴",
        "Kosovo": "🇽🇰",
    }
    if country in overrides:
        return overrides[country]
    try:
        import pycountry

        item = pycountry.countries.search_fuzzy(country)[0]
        return "".join(chr(127397 + ord(char)) for char in item.alpha_2.upper())
    except Exception:
        return "⚽"


def confidence_label(value: float) -> str:
    if value >= 0.72:
        return "High Confidence"
    if value >= 0.55:
        return "Moderate Confidence"
    return "Low Confidence"


def form_html(profile):
    values = profile.get("recent_results", [])
    if not values:
        values = ["D"] * 5
    pills = "".join(f'<span class="form-pill {item}">{item}</span>' for item in values[-5:])
    return f"<div>{pills}</div>"


def probability_bar(label: str, value: float, tone: str = "primary"):
    pct = value * 100
    return f"""
    <div class="probability-line">
        <div class="probability-meta">
            <span>{escape(label)}</span>
            <strong>{pct:.1f}%</strong>
        </div>
        <div class="bar-bg"><div class="bar {tone}" style="width:{pct:.1f}%"></div></div>
    </div>
    """


def prediction_hero(team_a, team_b, winner_text, prediction_label, confidence, probabilities):
    outcome_labels = {
        "TeamA_Win": f"{team_a} Win",
        "Draw": "Draw",
        "TeamB_Win": f"{team_b} Win",
    }
    bars = "".join(
        probability_bar(outcome_labels[key], probabilities[key], "muted" if key != prediction_label else "primary")
        for key in ["TeamA_Win", "Draw", "TeamB_Win"]
    )
    winner_flag = "" if winner_text == "Draw" else f'<span class="result-flag">{flag_for(winner_text)}</span>'
    probability = confidence * 100
    return f"""
    <div class="prediction-hero-card">
        <div class="prediction-copy">
            <div class="prediction-title">{winner_flag}<span>{escape(winner_text)}</span></div>
            <div class="prediction-probability">{probability:.1f}%</div>
            <div class="prediction-subtitle">{escape(confidence_label(confidence))}</div>
        </div>
        <div class="probability-stack">
            {bars}
        </div>
    </div>
    """


def prediction_reasons(team_a, team_b, features):
    reasons = []
    if features["rank_diff"] > 0:
        reasons.append(f"{team_a} has the stronger FIFA ranking profile.")
    elif features["rank_diff"] < 0:
        reasons.append(f"{team_b} has the stronger FIFA ranking profile.")

    if features["form_diff"] > 0.08:
        reasons.append(f"{team_a} enters with better recent form.")
    elif features["form_diff"] < -0.08:
        reasons.append(f"{team_b} enters with better recent form.")
    else:
        reasons.append("Recent form is close across the last five matches.")

    if features["goals_for_diff"] > 0.2:
        reasons.append(f"{team_a} has produced more goals recently.")
    elif features["goals_for_diff"] < -0.2:
        reasons.append(f"{team_b} has produced more goals recently.")

    if features["goal_diff_delta"] > 0.2:
        reasons.append(f"{team_a} carries the better goal-difference trend.")
    elif features["goal_diff_delta"] < -0.2:
        reasons.append(f"{team_b} carries the better goal-difference trend.")

    if features["h2h_meetings"] > 0:
        if features["h2h_goal_diff"] > 0:
            reasons.append(f"{team_a} has a positive head-to-head goal edge.")
        elif features["h2h_goal_diff"] < 0:
            reasons.append(f"{team_b} has a positive head-to-head goal edge.")

    if len(reasons) < 3:
        reasons.append("The model is weighing both ranking and recent performance signals.")

    items = "".join(f'<li><span class="reason-icon">✓</span><span>{escape(reason)}</span></li>' for reason in reasons[:5])
    return f"""
    <section class="clean-section">
        <div class="section-heading">Why This Prediction?</div>
        <ul class="reason-list">{items}</ul>
    </section>
    """


def _score_bar(value: float, maximum: float = 1.0, inverse: bool = False) -> float:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return 0
    pct = max(0, min(100, (float(value) / maximum) * 100))
    return 100 - pct if inverse else pct


def stat_row(label: str, left_label: str, right_label: str, left_value, right_value, left_pct: float, right_pct: float):
    return f"""
    <div class="comparison-row">
        <div class="comparison-topline">
            <span>{escape(label)}</span>
            <strong>{escape(str(left_value))} <span>vs</span> {escape(str(right_value))}</strong>
        </div>
        <div class="split-bars">
            <div class="split-side left"><div style="width:{left_pct:.1f}%"></div></div>
            <div class="split-side right"><div style="width:{right_pct:.1f}%"></div></div>
        </div>
        <div class="comparison-labels"><span>{escape(left_label)}</span><span>{escape(right_label)}</span></div>
    </div>
    """


def comparison_html(team_a, team_b, rank_a, rank_b, profile_a, profile_b):
    max_rank = max(float(rank_a or 0), float(rank_b or 0), 1)
    max_goals = max(profile_a.get("avg_goals_for", 0), profile_b.get("avg_goals_for", 0), 1)
    max_defense = max(profile_a.get("avg_goals_against", 0), profile_b.get("avg_goals_against", 0), 1)
    max_goal_diff = max(abs(profile_a.get("goal_diff", 0)), abs(profile_b.get("goal_diff", 0)), 1)
    rows = [
        stat_row(
            "FIFA ranking",
            team_a,
            team_b,
            f"#{int(rank_a)}" if rank_a else "N/A",
            f"#{int(rank_b)}" if rank_b else "N/A",
            _score_bar(rank_a, max_rank, inverse=True),
            _score_bar(rank_b, max_rank, inverse=True),
        ),
        stat_row(
            "Recent win rate",
            team_a,
            team_b,
            f"{profile_a.get('win_pct', 0) * 100:.0f}%",
            f"{profile_b.get('win_pct', 0) * 100:.0f}%",
            _score_bar(profile_a.get("win_pct", 0)),
            _score_bar(profile_b.get("win_pct", 0)),
        ),
        stat_row(
            "Scoring form",
            team_a,
            team_b,
            f"{profile_a.get('avg_goals_for', 0):.2f}",
            f"{profile_b.get('avg_goals_for', 0):.2f}",
            _score_bar(profile_a.get("avg_goals_for", 0), max_goals),
            _score_bar(profile_b.get("avg_goals_for", 0), max_goals),
        ),
        stat_row(
            "Defensive control",
            team_a,
            team_b,
            f"{profile_a.get('avg_goals_against', 0):.2f}",
            f"{profile_b.get('avg_goals_against', 0):.2f}",
            _score_bar(profile_a.get("avg_goals_against", 0), max_defense, inverse=True),
            _score_bar(profile_b.get("avg_goals_against", 0), max_defense, inverse=True),
        ),
        stat_row(
            "Goal difference",
            team_a,
            team_b,
            f"{profile_a.get('goal_diff', 0):+.2f}",
            f"{profile_b.get('goal_diff', 0):+.2f}",
            _score_bar(abs(profile_a.get("goal_diff", 0)), max_goal_diff),
            _score_bar(abs(profile_b.get("goal_diff", 0)), max_goal_diff),
        ),
    ]

    return f"""
    <section class="clean-section">
        <div class="section-heading">Team Comparison</div>
        <div class="comparison-shell">
            <div class="team-strip">
                <div><span class="team-chip">{flag_for(team_a)} {escape(team_a)}</span>{form_html(profile_a)}</div>
                <div><span class="team-chip">{flag_for(team_b)} {escape(team_b)}</span>{form_html(profile_b)}</div>
            </div>
            {''.join(rows)}
        </div>
    </section>
    """
