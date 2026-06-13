# World Cup Oracle

World Cup Oracle is a production-style Streamlit application that predicts outcomes for international football matches using historical FIFA match results, FIFA ranking timelines, recent team form, goal trends, head-to-head history, and tournament context.

<img width="1857" height="860" alt="image" src="https://github.com/user-attachments/assets/b9118f59-45b1-42ab-a00d-3e79be9d19de" />
<img width="1007" height="852" alt="image" src="https://github.com/user-attachments/assets/283b843d-316f-4c37-ac0a-4d63b1b7aa32" />
<img width="1027" height="708" alt="image" src="https://github.com/user-attachments/assets/803a5551-e581-4d8d-bdb6-d05089d88356" />



## Features

- Predicts Team A win, draw, and Team B win probabilities
- Displays predicted outcome and confidence score
- Explains key factors behind each forecast
- Compares FIFA ranking, recent form, win rate, and goal trends
- Shows recent form indicators and feature importance
- Uses a time-aware ML pipeline to avoid future-data leakage

## Tech Stack

- Python, Pandas, NumPy
- Scikit-learn
- Joblib
- Streamlit
- Plotly
- Custom CSS

## Project Structure

```text
world-cup-oracle/
├── app.py
├── train_model.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── models/
│   └── predictor.pkl
├── assets/
├── components/
├── utils/
└── notebooks/
```

## Datasets

The training script downloads and caches public datasets:

- International football results: `martj42/international_results`
- Historical FIFA rankings: `Dato-Futbol/fifa-ranking`

Ranking features are attached using the latest ranking record available on or before the match date. Rolling form, goal statistics, and head-to-head features are calculated only from matches played before each training example.

## Model

The pipeline evaluates:

- Logistic Regression
- Gradient Boosting Classifier
- Random Forest Classifier

Models are evaluated with a time-based split using accuracy, weighted precision, weighted recall, weighted F1, and a confusion matrix. The best model by weighted F1 is retrained on the full leakage-safe feature frame and saved to `models/predictor.pkl`.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
streamlit run app.py
```

## Deployment

For Streamlit Community Cloud or similar platforms:

1. Push the repository to GitHub.
2. Set `app.py` as the Streamlit entry point.
3. Ensure `requirements.txt` is included.
4. Either commit `models/predictor.pkl` or run `python train_model.py` as part of the deployment build process.

## Future Improvements

- Add betting-market calibration and reliability curves
- Add Elo ratings and squad-strength features
- Include confederation, travel distance, and rest-day context
- Add World Cup bracket simulation
- Add model monitoring for probability drift
