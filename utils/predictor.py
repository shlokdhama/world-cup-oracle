import joblib
import pandas as pd

from utils.constants import MODEL_PATH
from utils.features import make_prediction_features


def load_bundle(path=MODEL_PATH):
    return joblib.load(path)


def predict_match(bundle, team_a: str, team_b: str):
    features = make_prediction_features(
        team_a,
        team_b,
        bundle["rankings"],
        bundle["team_profiles"],
        bundle.get("h2h_profiles"),
    )
    model = bundle["model"]
    probabilities = model.predict_proba(features)[0]
    classes = list(model.classes_)
    prob_map = {label: float(probabilities[classes.index(label)]) for label in classes}
    ordered = {
        "TeamA_Win": prob_map.get("TeamA_Win", 0.0),
        "Draw": prob_map.get("Draw", 0.0),
        "TeamB_Win": prob_map.get("TeamB_Win", 0.0),
    }
    winner_label = max(ordered, key=ordered.get)
    confidence = ordered[winner_label]
    return {
        "features": features.iloc[0],
        "probabilities": ordered,
        "prediction": winner_label,
        "confidence": confidence,
    }


def feature_importance_frame(bundle) -> pd.DataFrame:
    data = bundle.get("feature_importance", [])
    return pd.DataFrame(data).head(12)
