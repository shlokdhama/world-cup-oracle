from collections import defaultdict, deque
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

from utils.constants import FEATURE_COLUMNS


MAJOR_TOURNAMENTS = {
    "FIFA World Cup",
    "UEFA Euro",
    "Copa América",
    "AFC Asian Cup",
    "African Cup of Nations",
    "CONCACAF Gold Cup",
    "Oceania Nations Cup",
}


def tournament_type(name: str) -> str:
    if name == "Friendly":
        return "Friendly"
    if name in MAJOR_TOURNAMENTS:
        return "Major tournament"
    if "qualification" in str(name).lower() or "qualifying" in str(name).lower():
        return "Qualifier"
    return "Other competition"


def _default_form() -> Dict[str, float]:
    return {
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "form_score": 0.0,
        "win_pct": 0.0,
        "avg_goals_for": 0.0,
        "avg_goals_against": 0.0,
        "goal_diff": 0.0,
    }


def summarize_matches(matches: Iterable[Tuple[int, int]]) -> Dict[str, float]:
    rows = list(matches)
    if not rows:
        return _default_form()

    wins = sum(1 for gf, ga in rows if gf > ga)
    draws = sum(1 for gf, ga in rows if gf == ga)
    losses = sum(1 for gf, ga in rows if gf < ga)
    goals_for = np.mean([gf for gf, _ in rows])
    goals_against = np.mean([ga for _, ga in rows])
    played = len(rows)
    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "form_score": (3 * wins + draws) / max(played * 3, 1),
        "win_pct": wins / played,
        "avg_goals_for": goals_for,
        "avg_goals_against": goals_against,
        "goal_diff": goals_for - goals_against,
    }


def build_team_profiles(results: pd.DataFrame, as_of_date=None) -> Dict[str, Dict[str, object]]:
    cutoff = pd.Timestamp(as_of_date) if as_of_date is not None else results["date"].max()
    histories = defaultdict(lambda: deque(maxlen=5))
    for row in results[results["date"] < cutoff].sort_values("date").itertuples():
        histories[row.team_a].append((int(row.team_a_score), int(row.team_b_score)))
        histories[row.team_b].append((int(row.team_b_score), int(row.team_a_score)))

    profiles = {}
    for team, matches in histories.items():
        profile = summarize_matches(matches)
        profile["recent_results"] = [
            "W" if gf > ga else "D" if gf == ga else "L"
            for gf, ga in list(matches)[-5:]
        ]
        profiles[team] = profile
    return profiles


def _pair_key(team_a: str, team_b: str) -> str:
    return "||".join(sorted((team_a, team_b)))


def build_h2h_profiles(results: pd.DataFrame, as_of_date=None) -> Dict[str, List[Tuple[str, str, int, int]]]:
    cutoff = pd.Timestamp(as_of_date) if as_of_date is not None else results["date"].max() + pd.Timedelta(days=1)
    profiles = defaultdict(list)
    for row in results[results["date"] < cutoff].sort_values("date").itertuples():
        profiles[_pair_key(row.team_a, row.team_b)].append(
            (row.team_a, row.team_b, int(row.team_a_score), int(row.team_b_score))
        )
    return dict(profiles)


def attach_rankings_asof(results: pd.DataFrame, rankings: pd.DataFrame) -> pd.DataFrame:
    def merge_side(frame: pd.DataFrame, side: str) -> pd.DataFrame:
        left = frame[["date", side]].rename(columns={side: "team"}).reset_index()
        left = left.sort_values("date")
        merged = pd.merge_asof(
            left,
            rankings.sort_values("rank_date"),
            by="team",
            left_on="date",
            right_on="rank_date",
            direction="backward",
        ).set_index("index")
        return merged[["rank", "points"]].rename(columns={"rank": f"{side}_rank", "points": f"{side}_points"})

    ranked = results.copy()
    ranked = ranked.join(merge_side(ranked, "team_a")).join(merge_side(ranked, "team_b"))
    return ranked


def build_training_frame(results: pd.DataFrame, rankings: pd.DataFrame) -> pd.DataFrame:
    matches = attach_rankings_asof(results, rankings).sort_values("date").reset_index(drop=True)
    histories = defaultdict(lambda: deque(maxlen=5))
    h2h = defaultdict(list)
    rows: List[Dict[str, object]] = []

    for match in matches.itertuples(index=False):
        team_a, team_b = match.team_a, match.team_b
        a_form = summarize_matches(histories[team_a])
        b_form = summarize_matches(histories[team_b])
        key = tuple(sorted((team_a, team_b)))
        prior_h2h = h2h[key]
        a_h2h_wins = sum(1 for a, b, ag, bg in prior_h2h if (a == team_a and ag > bg) or (b == team_a and bg > ag))
        b_h2h_wins = sum(1 for a, b, ag, bg in prior_h2h if (a == team_b and ag > bg) or (b == team_b and bg > ag))
        h2h_draws = sum(1 for _, _, ag, bg in prior_h2h if ag == bg)
        h2h_goal_diff = sum((ag - bg) if a == team_a else (bg - ag) for a, b, ag, bg in prior_h2h)

        row = {
            "date": match.date,
            "team_a": team_a,
            "team_b": team_b,
            "tournament": match.tournament,
            "tournament_type": tournament_type(match.tournament),
            "neutral": int(match.neutral),
            "team_a_rank": match.team_a_rank,
            "team_b_rank": match.team_b_rank,
            "rank_diff": match.team_b_rank - match.team_a_rank,
            "team_a_points": match.team_a_points,
            "team_b_points": match.team_b_points,
            "points_diff": match.team_a_points - match.team_b_points,
            "team_a_h2h_wins": a_h2h_wins,
            "team_b_h2h_wins": b_h2h_wins,
            "h2h_draws": h2h_draws,
            "h2h_meetings": len(prior_h2h),
            "h2h_goal_diff": h2h_goal_diff,
        }

        for prefix, form in (("team_a", a_form), ("team_b", b_form)):
            for name, value in form.items():
                row[f"{prefix}_{name}"] = value

        row.update(
            {
                "form_diff": row["team_a_form_score"] - row["team_b_form_score"],
                "win_pct_diff": row["team_a_win_pct"] - row["team_b_win_pct"],
                "goals_for_diff": row["team_a_avg_goals_for"] - row["team_b_avg_goals_for"],
                "goals_against_diff": row["team_b_avg_goals_against"] - row["team_a_avg_goals_against"],
                "goal_diff_delta": row["team_a_goal_diff"] - row["team_b_goal_diff"],
                "target": "TeamA_Win"
                if match.team_a_score > match.team_b_score
                else "TeamB_Win"
                if match.team_a_score < match.team_b_score
                else "Draw",
            }
        )
        rows.append(row)

        histories[team_a].append((int(match.team_a_score), int(match.team_b_score)))
        histories[team_b].append((int(match.team_b_score), int(match.team_a_score)))
        h2h[key].append((team_a, team_b, int(match.team_a_score), int(match.team_b_score)))

    frame = pd.DataFrame(rows)
    frame = frame[frame["date"] >= "1993-01-01"].copy()
    frame[FEATURE_COLUMNS] = frame[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)
    return frame


def latest_rankings(rankings: pd.DataFrame) -> pd.DataFrame:
    return rankings.sort_values("rank_date").groupby("team", as_index=False).tail(1).set_index("team")


def summarize_h2h(team_a: str, team_b: str, h2h_profiles: Dict[str, List[Tuple[str, str, int, int]]] | None) -> Dict[str, int]:
    prior_h2h = (h2h_profiles or {}).get(_pair_key(team_a, team_b), [])
    a_wins = sum(1 for a, b, ag, bg in prior_h2h if (a == team_a and ag > bg) or (b == team_a and bg > ag))
    b_wins = sum(1 for a, b, ag, bg in prior_h2h if (a == team_b and ag > bg) or (b == team_b and bg > ag))
    draws = sum(1 for _, _, ag, bg in prior_h2h if ag == bg)
    goal_diff = sum((ag - bg) if a == team_a else (bg - ag) for a, b, ag, bg in prior_h2h)
    return {
        "h2h_meetings": len(prior_h2h),
        "team_a_h2h_wins": a_wins,
        "team_b_h2h_wins": b_wins,
        "h2h_draws": draws,
        "h2h_goal_diff": goal_diff,
    }


def make_prediction_features(
    team_a: str,
    team_b: str,
    rankings: pd.DataFrame,
    profiles: Dict[str, Dict[str, object]],
    h2h_profiles: Dict[str, List[Tuple[str, str, int, int]]] | None = None,
) -> pd.DataFrame:
    latest = latest_rankings(rankings)
    a_profile = profiles.get(team_a, _default_form())
    b_profile = profiles.get(team_b, _default_form())
    a_rank = float(latest.loc[team_a, "rank"]) if team_a in latest.index else np.nan
    b_rank = float(latest.loc[team_b, "rank"]) if team_b in latest.index else np.nan
    a_points = float(latest.loc[team_a, "points"]) if team_a in latest.index else np.nan
    b_points = float(latest.loc[team_b, "points"]) if team_b in latest.index else np.nan
    h2h_summary = summarize_h2h(team_a, team_b, h2h_profiles)

    row = {
        "team_a_rank": a_rank,
        "team_b_rank": b_rank,
        "rank_diff": b_rank - a_rank,
        "team_a_points": a_points,
        "team_b_points": b_points,
        "points_diff": a_points - b_points,
        **h2h_summary,
        "neutral": 1,
        "tournament_type": "Major tournament",
    }
    for prefix, form in (("team_a", a_profile), ("team_b", b_profile)):
        for name in ["form_score", "win_pct", "avg_goals_for", "avg_goals_against", "goal_diff"]:
            row[f"{prefix}_{name}"] = float(form.get(name, 0))

    row.update(
        {
            "form_diff": row["team_a_form_score"] - row["team_b_form_score"],
            "win_pct_diff": row["team_a_win_pct"] - row["team_b_win_pct"],
            "goals_for_diff": row["team_a_avg_goals_for"] - row["team_b_avg_goals_for"],
            "goals_against_diff": row["team_b_avg_goals_against"] - row["team_a_avg_goals_against"],
            "goal_diff_delta": row["team_a_goal_diff"] - row["team_b_goal_diff"],
        }
    )
    return pd.DataFrame([row])[FEATURE_COLUMNS]
