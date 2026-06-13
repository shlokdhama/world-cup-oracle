import plotly.express as px
import streamlit as st

from components.styles import inject_css
from components.ui import comparison_html, prediction_hero, prediction_reasons
from utils.constants import MODEL_PATH
from utils.features import latest_rankings
from utils.predictor import feature_importance_frame, load_bundle, predict_match


st.set_page_config(page_title="World Cup Oracle", page_icon=":soccer:", layout="wide")
inject_css(st)


@st.cache_resource(show_spinner=False)
def cached_bundle():
    if not MODEL_PATH.exists():
        st.error("Model bundle not found. Run `python train_model.py` first.")
        st.stop()
    return load_bundle()


bundle = cached_bundle()
rankings = latest_rankings(bundle["rankings"])
profiles = bundle["team_profiles"]
teams = [team for team in bundle["teams"] if team in rankings.index]

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">International football intelligence</div>
        <div class="title">WORLD CUP ORACLE</div>
        <div class="subtitle">AI-powered football match prediction platform</div>
        <p class="description">Predict international football matches using machine learning, historical FIFA results,
        ranking timelines, recent form, goal trends, and matchup context.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">Select Matchup</div>', unsafe_allow_html=True)
left, mid, right = st.columns([5, 1, 5], vertical_alignment="center")
default_a = teams.index("Brazil") if "Brazil" in teams else 0
default_b = teams.index("Argentina") if "Argentina" in teams else min(1, len(teams) - 1)
with left:
    team_a = st.selectbox("Team A", teams, index=default_a)
with mid:
    st.markdown('<div class="vs">VS</div>', unsafe_allow_html=True)
with right:
    team_b = st.selectbox("Team B", teams, index=default_b)

if team_a == team_b:
    st.warning("Select two different national teams.")
    st.stop()

a_rank = rankings.loc[team_a, "rank"] if team_a in rankings.index else None
b_rank = rankings.loc[team_b, "rank"] if team_b in rankings.index else None
a_profile = profiles.get(team_a, {})
b_profile = profiles.get(team_b, {})

predict_clicked = st.button("Predict Match Outcome")

if predict_clicked:
    outcome = predict_match(bundle, team_a, team_b)
    probs = outcome["probabilities"]
    winner_text = team_a if outcome["prediction"] == "TeamA_Win" else team_b if outcome["prediction"] == "TeamB_Win" else "Draw"

    st.html(
        prediction_hero(
            team_a=team_a,
            team_b=team_b,
            winner_text=winner_text,
            prediction_label=outcome["prediction"],
            confidence=outcome["confidence"],
            probabilities=probs,
        )
    )

    st.html(prediction_reasons(team_a, team_b, outcome["features"]))
    st.html(comparison_html(team_a, team_b, a_rank, b_rank, a_profile, b_profile))

    with st.expander("Advanced Analytics", expanded=False):
        st.caption("Feature importance from the selected model. These signals are shown for transparency, not as the primary product experience.")
        importance = feature_importance_frame(bundle)
        if not importance.empty:
            fig = px.bar(importance.sort_values("importance"), x="importance", y="feature", orientation="h", template="plotly_dark")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=430,
                margin=dict(l=10, r=10, t=20, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Feature importance is available when the selected model exposes tree-based importances.")

st.caption(
    f"Model: {bundle['model_name']} | Training rows: {bundle['trained_on_rows']:,} | Latest results data: {bundle['data_max_date']}"
)
