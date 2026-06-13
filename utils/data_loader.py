import pandas as pd

from utils.constants import RAW_DIR, RANKINGS_PATH, RANKINGS_URL, RESULTS_PATH, RESULTS_URL


def ensure_raw_data(force: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if force or not RESULTS_PATH.exists():
        pd.read_csv(RESULTS_URL).to_csv(RESULTS_PATH, index=False)
    if force or not RANKINGS_PATH.exists():
        pd.read_csv(RANKINGS_URL).to_csv(RANKINGS_PATH, index=False)


def load_results() -> pd.DataFrame:
    ensure_raw_data()
    results = pd.read_csv(RESULTS_PATH, parse_dates=["date"])
    results = results.dropna(subset=["home_score", "away_score"])
    results = results.rename(
        columns={
            "home_team": "team_a",
            "away_team": "team_b",
            "home_score": "team_a_score",
            "away_score": "team_b_score",
        }
    )
    results["neutral"] = results["neutral"].astype(int)
    return results


def load_rankings() -> pd.DataFrame:
    ensure_raw_data()
    rankings = pd.read_csv(RANKINGS_PATH)
    date_col = "date" if "date" in rankings.columns else "rank_date"
    team_col = "team" if "team" in rankings.columns else "country_full"
    rank_col = "rank" if "rank" in rankings.columns else "rank_country" if "rank_country" in rankings.columns else None
    points_col = "total_points" if "total_points" in rankings.columns else None

    rename_map = {date_col: "rank_date", team_col: "team"}
    if rank_col:
        rename_map[rank_col] = "rank"
    rankings = rankings.rename(columns=rename_map)
    rankings["rank_date"] = pd.to_datetime(rankings["rank_date"], errors="coerce")
    rankings["team"] = rankings["team"].replace(
        {
            "USA": "United States",
            "Korea Republic": "South Korea",
            "IR Iran": "Iran",
            "Türkiye": "Turkey",
            "Czechia": "Czech Republic",
            "Côte d'Ivoire": "Ivory Coast",
        }
    )
    rankings["points"] = pd.to_numeric(rankings[points_col], errors="coerce") if points_col else 0.0
    if "rank" in rankings.columns:
        rankings["rank"] = pd.to_numeric(rankings["rank"], errors="coerce")
    else:
        rankings = rankings.sort_values(["rank_date", "points"], ascending=[True, False])
        rankings["rank"] = rankings.groupby("rank_date").cumcount() + 1
    rankings = rankings.dropna(subset=["rank_date", "team", "rank"]).sort_values(["team", "rank_date"])
    return rankings[["rank_date", "team", "rank", "points"]]
