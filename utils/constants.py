from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"

RESULTS_URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
RANKINGS_URL = "https://raw.githubusercontent.com/Dato-Futbol/fifa-ranking/refs/heads/master/ranking_fifa_historical.csv"

RESULTS_PATH = RAW_DIR / "international_results.csv"
RANKINGS_PATH = RAW_DIR / "fifa_rankings.csv"
MODEL_PATH = MODELS_DIR / "predictor.pkl"
METRICS_PATH = MODELS_DIR / "metrics.json"

TARGET_LABELS = ["TeamA_Win", "Draw", "TeamB_Win"]

NUMERIC_FEATURES = [
    "team_a_rank",
    "team_b_rank",
    "rank_diff",
    "team_a_points",
    "team_b_points",
    "points_diff",
    "team_a_form_score",
    "team_b_form_score",
    "form_diff",
    "team_a_win_pct",
    "team_b_win_pct",
    "win_pct_diff",
    "team_a_avg_goals_for",
    "team_b_avg_goals_for",
    "goals_for_diff",
    "team_a_avg_goals_against",
    "team_b_avg_goals_against",
    "goals_against_diff",
    "team_a_goal_diff",
    "team_b_goal_diff",
    "goal_diff_delta",
    "h2h_meetings",
    "team_a_h2h_wins",
    "team_b_h2h_wins",
    "h2h_draws",
    "h2h_goal_diff",
    "neutral",
]

CATEGORICAL_FEATURES = ["tournament_type"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
