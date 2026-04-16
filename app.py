import streamlit as st
import pandas as pd
import numpy as np

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Cyclone Risk",
    page_icon="🌀",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1.5rem 4rem; max-width: 760px; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #01244a 0%, #5c8bb4 60%, #0085ca 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-icon { font-size: 3rem; margin-bottom: 0.5rem; }
.hero h1 {
    color: #f0f9ff;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.hero p {
    color: #94a3b8;
    font-size: 0.92rem;
    margin: 0;
}
.hero .badge {
    display: inline-block;
    background: rgba(56,189,248,0.15);
    color: #38bdf8;
    border: 1px solid rgba(56,189,248,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 500;
    margin-top: 0.8rem;
    letter-spacing: 0.03em;
}

/* ── Search box ── */
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 0.75rem 1rem !important;
    font-size: 1.1rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #0085ca
box-shadow: 0 0 0 3px rgba(0,133,202,0.15)
    box-shadow: 0 0 0 3px rgba(56,189,248,0.15) !important;
}

/* ── Score card ── */
.score-card {
    border-radius: 14px;
    padding: 1.75rem;
    margin: 1.25rem 0;
    border: 1px solid;
}
.score-card.very-high {
    background: #fff5f5;
    border-color: #fca5a5;
}
.score-card.high {
    background: #fff7ed;
    border-color: #fdba74;
}
.score-card.moderate {
    background: #fefce8;
    border-color: #fde047;
}
.score-card.low {
    background: #f0fdf4;
    border-color: #86efac;
}
.score-card.very-low {
    background: #f0f9ff;
    border-color: #7dd3fc;
}

.score-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.score-number {
    font-size: 3.2rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.04em;
}
.score-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.6;
    margin-top: 0.2rem;
}
.risk-badge {
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.35rem 0.9rem;
    border-radius: 20px;
    letter-spacing: 0.03em;
}
.badge-very-high { background: #fee2e2; color: #b91c1c; }
.badge-high      { background: #ffedd5; color: #c2410c; }
.badge-moderate  { background: #fef9c3; color: #a16207; }
.badge-low       { background: #dcfce7; color: #15803d; }
.badge-very-low  { background: #e0f2fe; color: #0369a1; }

/* Score bar */
.bar-wrap {
    background: #e2e8f0;
    border-radius: 6px;
    height: 8px;
    margin: 0.6rem 0 1.2rem;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 6px;
    transition: width 0.6s ease;
}
.bar-very-high { background: linear-gradient(90deg, #f87171, #dc2626); }
.bar-high      { background: linear-gradient(90deg, #fb923c, #ea580c); }
.bar-moderate  { background: linear-gradient(90deg, #facc15, #ca8a04); }
.bar-low       { background: linear-gradient(90deg, #4ade80, #16a34a); }
.bar-very-low  { background: linear-gradient(90deg, #38bdf8, #0284c7); }

/* Explanation */
.explanation {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.65;
    padding: 0.9rem 1rem;
    background: rgba(0,0,0,0.03);
    border-radius: 8px;
    border-left: 3px solid currentColor;
    margin-top: 0.5rem;
}

/* ── Indicator grid ── */
.indicators {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.8rem;
    margin: 1.2rem 0;
}
.ind-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}
.ind-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
}
.ind-label {
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #94a3b8;
    margin-top: 0.2rem;
}
.ind-sub {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.15rem;
}

/* ── Location pill ── */
.location-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #dee7f0;
    border: 1px solid #5c8bb4;
    border-radius: 20px;
    padding: 0.35rem 0.9rem;
    font-size: 0.82rem;
    color: #01244a;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* ── Methodology box ── */
.method-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 2rem;
}
.method-box h4 {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin: 0 0 0.75rem;
}
.method-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.45rem 0;
    border-bottom: 1px solid #e2e8f0;
    font-size: 0.84rem;
}
.method-row:last-child { border-bottom: none; }
.method-name { color: #334155; font-weight: 500; }
.method-weight {
    background: #01244a;
    color: white;
    border-radius: 12px;
    padding: 0.15rem 0.6rem;
    font-size: 0.75rem;
    font-weight: 600;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.78rem;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
    line-height: 1.8;
}
.footer a { color: #0085ca; text-decoration: none; }

/* ── Error ── */
.error-box {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    color: #991b1b;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

.stButton>button {
    background-color: #01244a;
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #0085ca;
    color: white;
}

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("precomputed_cyclone_scores.csv")
    df["pincode"] = df["pincode"].astype(str).str.strip().str.zfill(6)
    return df

df_scores = load_data()

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-icon">🌀</div>
    <h1>India Cyclone Risk Explorer</h1>
    <p>PIN code–level cyclone hazard scores derived from 180+ years of NOAA storm data</p>
    <div class="badge">NOAA IBTrACS · 1842–2023 · 19,550 PIN codes</div>
</div>
""", unsafe_allow_html=True)

# ── SEARCH ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    pin_input = st.text_input(
        label="PIN code",
        placeholder="Enter a 6-digit PIN code (e.g. 751001)",
        label_visibility="collapsed",
        max_chars=6,
    )
with col2:
    search = st.button("Search →", use_container_width=True, type="primary")

# ── LOOKUP ─────────────────────────────────────────────────────────────────────
def get_risk_class(level):
    return level.lower().replace(" ", "-")

def render_result(pin):
    pin_str = str(pin).strip().zfill(6)
    row = df_scores[df_scores["pincode"] == pin_str]

    if row.empty:
        st.markdown("""
        <div class="error-box">
            ⚠️ PIN code not found in database. Please check the number and try again.
        </div>
        """, unsafe_allow_html=True)
        return

    r = row.iloc[0]
    score     = float(r["cyclone_score"])
    level     = str(r["risk_level"])
    expl      = str(r["cyclone_explanation"])
    tc        = int(r["track_count"])
    wind      = float(r["max_wind"])
    decay     = float(r["decay_score"])
    state     = str(r["statename"]).title()
    district  = str(r["district"]).title()
    rc        = get_risk_class(level)

    # Location pill
    st.markdown(f"""
    <div class="location-pill">
        📍 {district}, {state} &nbsp;·&nbsp; PIN {pin_str}
    </div>
    """, unsafe_allow_html=True)

    # Main score card
    st.markdown(f"""
    <div class="score-card {rc}">
        <div class="score-header">
            <div>
                <div class="score-number">{score:.1f}</div>
                <div class="score-label">Cyclone Score / 100</div>
            </div>
            <span class="risk-badge badge-{rc}">{level} Risk</span>
        </div>
        <div class="bar-wrap">
            <div class="bar-fill bar-{rc}" style="width:{score}%"></div>
        </div>
        <div class="explanation">{expl}</div>
    </div>
    """, unsafe_allow_html=True)

    # Three indicator cards
    wind_display = f"{wind:.0f} kt" if wind > 0 else "None recorded"
    st.markdown(f"""
    <div class="indicators">
        <div class="ind-card">
            <div class="ind-value">{tc:,}</div>
            <div class="ind-label">Track Points</div>
            <div class="ind-sub">within 200 km</div>
        </div>
        <div class="ind-card">
            <div class="ind-value">{wind_display}</div>
            <div class="ind-label">Max Wind</div>
            <div class="ind-sub">1-min sustained</div>
        </div>
        <div class="ind-card">
            <div class="ind-value">{decay:.3f}</div>
            <div class="ind-label">Decay Index</div>
            <div class="ind-sub">proximity-weighted</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Run lookup
if pin_input and (search or len(pin_input) == 6):
    if not pin_input.isdigit() or len(pin_input) != 6:
        st.markdown("""
        <div class="error-box">
            ⚠️ Please enter a valid 6-digit PIN code containing only numbers.
        </div>
        """, unsafe_allow_html=True)
    else:
        render_result(pin_input)

# ── METHODOLOGY ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="method-box">
    <h4>How the score is calculated</h4>
    <div class="method-row">
        <span class="method-name">🌀 Track density &nbsp;<span style="color:#94a3b8;font-weight:400;font-size:0.8rem">— storm track points within 200 km</span></span>
        <span class="method-weight">40%</span>
    </div>
    <div class="method-row">
        <span class="method-name">💨 Max wind exposure &nbsp;<span style="color:#94a3b8;font-weight:400;font-size:0.8rem">— highest 1-min wind within 200 km</span></span>
        <span class="method-weight">35%</span>
    </div>
    <div class="method-row">
        <span class="method-name">📡 Distance-decayed exposure &nbsp;<span style="color:#94a3b8;font-weight:400;font-size:0.8rem">— wind / distance² summed, log-scaled</span></span>
        <span class="method-weight">25%</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Data source: <a href="https://www.ncei.noaa.gov/products/international-best-track-archive" target="_blank">NOAA IBTrACS v04</a>
    (International Best Track Archive for Climate Stewardship) · Public domain<br>
    PIN code coordinates: India Post via Open Government Data Platform India · GOI Open Data License<br>
    Scores are historical hazard estimates only and do not constitute official risk assessments.
</div>
""", unsafe_allow_html=True)
