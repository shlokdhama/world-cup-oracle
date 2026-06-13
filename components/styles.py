def inject_css(st):
    st.markdown(
        """
        <style>
        :root {
            --bg: #07111f;
            --panel: rgba(255, 255, 255, 0.075);
            --line: rgba(255, 255, 255, 0.14);
            --text: #f8fbff;
            --muted: #98a7bb;
            --cyan: #4de3ff;
            --green: #3ff3a3;
            --gold: #ffd166;
            --red: #ff6b7a;
        }
        .stApp {
            background:
                radial-gradient(circle at 15% 10%, rgba(77, 227, 255, 0.16), transparent 28%),
                radial-gradient(circle at 88% 22%, rgba(63, 243, 163, 0.12), transparent 30%),
                linear-gradient(135deg, #050b16 0%, #07111f 48%, #0a1729 100%);
            color: var(--text);
        }
        [data-testid="stSidebar"], header, footer {display: none !important;}
        .block-container {max-width: 1080px; padding: 2.4rem 1.35rem 5rem;}
        h1, h2, h3, p, label, span {font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
        .hero {
            padding: 3.3rem 0 2.4rem;
            margin-bottom: 1.7rem;
        }
        .eyebrow {color: var(--cyan); text-transform: uppercase; font-size: 0.78rem; font-weight: 800; letter-spacing: 0.16em;}
        .title {font-size: clamp(3rem, 8vw, 7rem); line-height: .86; font-weight: 950; margin: .45rem 0; letter-spacing: 0;}
        .subtitle {font-size: clamp(1.25rem, 2vw, 1.7rem); color: #d8e3f2; margin-bottom: .6rem;}
        .description {max-width: 720px; color: var(--muted); font-size: 1.02rem;}
        .glass {
            background: var(--panel);
            border: 1px solid rgba(255, 255, 255, 0.09);
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.22);
            backdrop-filter: blur(18px);
            border-radius: 8px;
            padding: 1rem;
        }
        .selector-shell {
            background: rgba(255,255,255,.055);
            border: 1px solid rgba(255,255,255,.09);
            border-radius: 8px;
            padding: 1rem 1rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 20px 60px rgba(0,0,0,.16);
        }
        .team-card {
            min-height: 156px;
            transition: transform .2s ease, border-color .2s ease, background .2s ease;
        }
        .team-card:hover {transform: translateY(-2px); border-color: rgba(77, 227, 255, .42);}
        .flag {font-size: 2.25rem;}
        .team-name {font-size: 1.55rem; font-weight: 850; margin-top: .25rem;}
        .metric-label {color: var(--muted); font-size: .78rem; text-transform: uppercase; font-weight: 800; letter-spacing: .08em;}
        .metric-value {font-size: 1.75rem; font-weight: 900;}
        .vs {text-align: center; font-weight: 950; color: var(--cyan); padding-top: 2.45rem; font-size: .95rem; letter-spacing:.14em;}
        .winner-card {padding: 1.35rem; border: 1px solid rgba(77, 227, 255, .28); background: linear-gradient(135deg, rgba(77, 227, 255, .14), rgba(255,255,255,.055)); border-radius: 8px;}
        .winner {font-size: clamp(1.85rem, 4vw, 3rem); font-weight: 950; margin: .2rem 0;}
        .prob-row, .probability-line {margin: .9rem 0;}
        .probability-meta, .comparison-topline, .comparison-labels {
            display:flex; justify-content:space-between; align-items:center; gap:1rem;
        }
        .probability-meta {font-size:.95rem; color:#dce7f4; margin-bottom:.42rem;}
        .probability-meta strong {font-size:1rem; color:#fff;}
        .bar-bg {height: 11px; border-radius: 999px; background: rgba(255,255,255,.1); overflow: hidden;}
        .bar {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--cyan), var(--green));
            animation: growBar .9s ease both;
            transform-origin: left center;
        }
        .bar.muted {background: linear-gradient(90deg, rgba(216,227,242,.55), rgba(152,167,187,.75));}
        @keyframes growBar {from {transform: scaleX(.08); opacity:.45;} to {transform: scaleX(1); opacity:1;}}
        .form-pill {display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; border-radius: 999px; margin-right: .35rem; font-weight: 900;}
        .W {background: rgba(63,243,163,.18); color: var(--green); border: 1px solid rgba(63,243,163,.35);}
        .D {background: rgba(255,209,102,.16); color: var(--gold); border: 1px solid rgba(255,209,102,.36);}
        .L {background: rgba(255,107,122,.15); color: var(--red); border: 1px solid rgba(255,107,122,.34);}
        .stButton button {
            width: 100%;
            min-height: 58px;
            border-radius: 8px;
            border: 1px solid rgba(77, 227, 255, .45);
            background: linear-gradient(135deg, #4de3ff, #3ff3a3);
            color: #04101c;
            font-weight: 950;
            font-size: 1rem;
            box-shadow: 0 16px 48px rgba(77, 227, 255, .2);
        }
        .stSelectbox div[data-baseweb="select"] > div {
            background: rgba(255,255,255,.08);
            border-color: rgba(255,255,255,.16);
            border-radius: 8px;
        }
        .prediction-hero-card {
            display:grid;
            grid-template-columns: minmax(0, 1.08fr) minmax(340px, .92fr);
            gap: clamp(1.8rem, 4.5vw, 3.6rem);
            align-items:center;
            min-height: clamp(430px, 48vw, 560px);
            margin: 2.2rem 0 2.6rem;
            padding: clamp(2.2rem, 5vw, 3.8rem);
            border-radius: 8px;
            background:
                linear-gradient(135deg, rgba(77,227,255,.16), rgba(63,243,163,.08) 44%, rgba(255,255,255,.055)),
                rgba(255,255,255,.06);
            border: 1px solid rgba(255,255,255,.11);
            box-shadow: 0 34px 120px rgba(0,0,0,.34);
            backdrop-filter: blur(22px);
        }
        .prediction-title {
            display:flex;
            align-items:center;
            gap:1rem;
            font-size: clamp(2.1rem, 5.3vw, 4.6rem);
            line-height:.88;
            font-weight: 950;
            margin:0 0 1.1rem;
        }
        .result-flag {font-size: clamp(2.4rem, 6vw, 5rem);}
        .prediction-probability {
            font-size: clamp(4.2rem, 11vw, 9.5rem);
            line-height:.82;
            font-weight: 950;
            color:#fff;
            letter-spacing:0;
            margin-bottom:1rem;
        }
        .prediction-subtitle {font-size: clamp(1.15rem, 2.2vw, 1.55rem); color:#eef6ff; font-weight:850;}
        .probability-stack {
            background: rgba(5, 11, 22, .34);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 8px;
            padding: 1.35rem 1.45rem;
        }
        .clean-section {margin: 1.8rem 0 2.2rem;}
        .section-heading {
            font-size: clamp(1.25rem, 2vw, 1.65rem);
            font-weight: 920;
            margin-bottom: .95rem;
        }
        .reason-list {
            display:grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap:.7rem;
            list-style:none;
            margin:0;
            padding:0;
        }
        .reason-list li {
            display:flex;
            align-items:flex-start;
            gap:.65rem;
            padding:.85rem .95rem;
            border-radius:8px;
            background: rgba(255,255,255,.055);
            color:#dce7f4;
        }
        .reason-icon {
            color:#04101c;
            background:linear-gradient(135deg, var(--cyan), var(--green));
            width:22px;
            height:22px;
            display:inline-flex;
            align-items:center;
            justify-content:center;
            border-radius:999px;
            font-weight:950;
            flex:0 0 22px;
        }
        .comparison-shell {
            background: rgba(255,255,255,.045);
            border-radius: 8px;
            padding: 1.1rem;
        }
        .team-strip {
            display:grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap:1rem;
            margin-bottom:1rem;
        }
        .team-strip > div {
            background: rgba(255,255,255,.045);
            border-radius:8px;
            padding:.95rem;
        }
        .team-chip {
            display:block;
            color:#fff;
            font-weight:900;
            margin-bottom:.85rem;
        }
        .comparison-row {
            padding: 1rem .25rem;
            border-top: 1px solid rgba(255,255,255,.075);
        }
        .comparison-topline {margin-bottom:.55rem;}
        .comparison-topline span:first-child {color:#dce7f4; font-weight:850;}
        .comparison-topline strong {color:#fff;}
        .comparison-topline strong span {color:var(--muted); font-size:.8rem; font-weight:700;}
        .split-bars {
            display:grid;
            grid-template-columns: 1fr 1fr;
            gap:.55rem;
        }
        .split-side {
            height:9px;
            border-radius:999px;
            background: rgba(255,255,255,.08);
            overflow:hidden;
        }
        .split-side div {height:100%; border-radius:999px; animation: growBar .9s ease both;}
        .split-side.left div {margin-left:auto; background:linear-gradient(90deg, rgba(77,227,255,.55), var(--cyan));}
        .split-side.right div {background:linear-gradient(90deg, var(--green), rgba(63,243,163,.55));}
        .comparison-labels {color:var(--muted); font-size:.8rem; margin-top:.42rem;}
        div[data-testid="stExpander"] {
            background: rgba(255,255,255,.04);
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 8px;
        }
        @media (max-width: 760px) {
            .prediction-hero-card {grid-template-columns: 1fr;}
            .reason-list {grid-template-columns: 1fr;}
            .team-strip {grid-template-columns: 1fr;}
            .vs {padding-top:.4rem; padding-bottom:.4rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
