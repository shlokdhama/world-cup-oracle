import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from utils.constants import CATEGORICAL_FEATURES, FEATURE_COLUMNS, METRICS_PATH, MODEL_PATH, MODELS_DIR, NUMERIC_FEATURES, PROCESSED_DIR
from utils.data_loader import load_rankings, load_results
from utils.features import build_h2h_profiles, build_team_profiles, build_training_frame


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("num", numeric, NUMERIC_FEATURES), ("cat", categorical, CATEGORICAL_FEATURES)])


def candidate_models():
    return {
        "LogisticRegression": LogisticRegression(max_iter=1200, class_weight="balanced", n_jobs=None),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=42),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=420,
            min_samples_leaf=5,
            max_depth=18,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
    }


def extract_feature_importance(model: Pipeline):
    classifier = model.named_steps["classifier"]
    if not hasattr(classifier, "feature_importances_"):
        return []
    names = model.named_steps["preprocessor"].get_feature_names_out()
    cleaned = [name.replace("num__", "").replace("cat__", "") for name in names]
    rows = sorted(zip(cleaned, classifier.feature_importances_), key=lambda item: item[1], reverse=True)
    return [{"feature": name, "importance": float(value)} for name, value in rows]


def train():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading datasets...")
    results = load_results()
    rankings = load_rankings()
    frame = build_training_frame(results, rankings).dropna(subset=["target"])
    frame.to_csv(PROCESSED_DIR / "training_features.csv", index=False)

    split_date = frame["date"].quantile(0.82)
    train_df = frame[frame["date"] <= split_date]
    test_df = frame[frame["date"] > split_date]
    x_train, y_train = train_df[FEATURE_COLUMNS], train_df["target"]
    x_test, y_test = test_df[FEATURE_COLUMNS], test_df["target"]

    results_by_model = {}
    fitted_models = {}
    for name, classifier in candidate_models().items():
        pipeline = Pipeline([("preprocessor", build_preprocessor()), ("classifier", classifier)])
        pipeline.fit(x_train, y_train)
        preds = pipeline.predict(x_test)
        results_by_model[name] = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, average="weighted", zero_division=0),
            "recall": recall_score(y_test, preds, average="weighted", zero_division=0),
            "f1": f1_score(y_test, preds, average="weighted", zero_division=0),
            "classification_report": classification_report(y_test, preds, zero_division=0, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, preds, labels=["TeamA_Win", "Draw", "TeamB_Win"]).tolist(),
        }
        fitted_models[name] = pipeline
        print(f"{name}: accuracy={results_by_model[name]['accuracy']:.3f}, f1={results_by_model[name]['f1']:.3f}")

    best_name = max(results_by_model, key=lambda name: results_by_model[name]["f1"])
    best_model = fitted_models[best_name]
    best_model.fit(frame[FEATURE_COLUMNS], frame["target"])

    profiles = build_team_profiles(results)
    h2h_profiles = build_h2h_profiles(results)
    bundle = {
        "model": best_model,
        "model_name": best_name,
        "feature_columns": FEATURE_COLUMNS,
        "metrics": results_by_model,
        "best_metrics": results_by_model[best_name],
        "feature_importance": extract_feature_importance(best_model),
        "rankings": rankings,
        "team_profiles": profiles,
        "h2h_profiles": h2h_profiles,
        "teams": sorted(set(results["team_a"]).intersection(set(rankings["team"]))),
        "trained_on_rows": int(len(frame)),
        "data_max_date": str(pd.to_datetime(results["date"]).max().date()),
    }
    joblib.dump(bundle, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps({"best_model": best_name, "models": results_by_model}, indent=2), encoding="utf-8")
    print(f"Saved model bundle to {MODEL_PATH}")
    print(f"Best model: {best_name}")
    print(json.dumps(results_by_model[best_name], indent=2)[:2200])


if __name__ == "__main__":
    train()
