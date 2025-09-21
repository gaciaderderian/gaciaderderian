import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lebanon's External Debt in USD: 1990-2024", page_icon="📈", layout="wide")

# =========================
# USER TEXT (from your brief)
# =========================
APP_TITLE = "Lebanon's External Debt in USD: 1990-2024"

INTRO_TEXT = """\
**THE DATA: LEBANON’S EXTERNAL DEBT IN USD**  
Rows: 2,112  
Columns: 9  
Publisher: The World Bank  
Geography: Lebanon  
ref Period (Year): 1960 → 2022 (range = 62 years)
"""

LINE_ANALYSIS = """\
- Debt stayed low until the early 1990s, then began rising sharply.  
- Rapid acceleration after 2005, peaking near 2018 (at $80B).  
- Recent years show a slowdown and slight decline.  
- At certain points, the dataset reports negative external debt values. This can be interpreted in three possible ways:
  1) **Data entry or collection error** — the negative may in fact represent a positive figure mistakenly recorded.  
  2) **Reverse flows of debt** — Lebanon may have acted as a creditor, providing loans or credit to other governments.  
  3) **Lending to non-residents** — the data could reflect financial assets extended abroad, though the dataset does not specify.
"""

LINE_WHY = """\
A line chart best shows trends and turning points over time.  
It highlights the pace of change more clearly than bars or pies.  
Simple, executive-friendly way to tell the debt growth story.
"""

SCATTER_ANALYSIS = """\
- **Magnitude at a glance:** Larger, turquoise points flag the highest debt years; smaller magenta points mark low periods.  
- **Clear outliers:** A few points sit well above the cloud but these are real, as Lebanon did take on that level of debt, so excluding them would distort accuracy.  
- **Non-uniform variance:** Spread widens in later years, hinting at greater volatility as debt levels rise.
"""

SCATTER_WHY = """\
**Best for relationships:** A scatter shows how debt evolves year by year while exposing outliers and scale in one view.  
**Color + size encode meaning:** The gradient (magenta → turquoise) makes magnitude and extremes obvious, faster than tables or bars.  
**Cleaner than alternatives:** A line hides distribution; a bar misses outliers; a box loses the *when*. Scatter balances time, level, and anomaly detection.
"""

# =========================
# DATA LOADING
# =========================
DEFAULT_CSV_PATH = "data/external_debt_dataset.csv"   # from you
YEAR_COL_CANDIDATES = ["year", "Year", "refPeriod", "ref period", "ref Period"]
DEBT_COL_CANDIDATES = ["External_Debt", "external_debt", "Value", "External Debt"]

st.sidebar.header("Data")
data_path = st.sidebar.text_input("Path to your CSV", DEFAULT_CSV_PATH)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize headers & drop accidental index columns
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
    return df

def find_col(df: pd.DataFrame, candidates) -> str | None:
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None

try:
    df = load_data(data_path)
except Exception as e:
    st.error(f"Couldn't load data from '{data_path}'. Error: {e}")
    st.stop()

# Resolve column names from your list
YEAR_COL = find_col(df, YEAR_COL_CANDIDATES) or "year"
DEBT_COL = find_col(df, DEBT_COL_CANDIDATES) or "External_Debt"
if YEAR_COL not in df.columns or DEBT_COL not in df.columns:
    st.error(f"Couldn't find expected columns for Year ('{YEAR_COL}') and Debt ('{DEBT_COL}') in the data.")
    st.stop()

# coerce types and clean
df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors="coerce")
df[DEBT_COL] = pd.to_numeric(df[DEBT_COL], errors="coerce")
df = df.dropna(subset=[YEAR_COL, DEBT_COL]).sort_values(YEAR_COL)

# =========================
# HEADER (CENTERED) + INTRO
# =========================
st.markdown(
    f"""
    <div style="text-align:center">
        <h1 style="margin-bottom:0.4rem">{APP_TITLE}</h1>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("### Introduction")
st.write(INTRO_TEXT)
st.markdown("---")

with st.expander("Preview data (first 5 rows)", expanded=False):
    st.dataframe(df.head())

# =========================
# FILTERS (INTERACTIVE)
# =========================
st.sidebar.header("Filters")

# Year range filter
min_year, max_year = int(df[YEAR_COL].min()), int(df[YEAR_COL].max())
year_range = st.sidebar.slider("Year range", min_year, max_year, (max(min_year, 1990), min(max_year, 2024)), step=1)

# Debt range (Y-axis) filter
debt_min_all, debt_max_all = float(df[DEBT_COL].min()), float(df[DEBT_COL].max())
debt_range = st.sidebar.slider(
    "Debt range (Y axis, in USD)",
    float(debt_min_all), float(debt_max_all),
    (float(debt_min_all), float(debt_max_all))
)
st.sidebar.caption(f"Current: ${debt_range[0]:,.0f} — ${debt_range[1]:,.0f}")

# Optional: y-axis scale toggle
use_log_y = st.sidebar.checkbox("Log scale (Y axis)", value=False)

# Apply filters
df_filt = df[
    (df[YEAR_COL] >= year_range[0]) & (df[YEAR_COL] <= year_range[1]) &
    (df[DEBT_COL] >= debt_range[0]) & (df[DEBT_COL] <= debt_range[1])
].copy()

if df_filt.empty:
    st.warning("No data in the selected filters. Try widening your year or debt range.")
    st.stop()

# =========================
# STYLE
# =========================
MAGENTA = "#a429aa"
COLORSCALE = [
    (0.00, "#a429aa"),
    (0.25, "#c868c9"),
    (0.50, "#e8c6e9"),
    (0.75, "#66d7d1"),
    (1.00, "#11c7c7"),
]

# =========================
# LAYOUT: TWO COLUMNS SIDE BY SIDE
# =========================
col1, col2 = st.columns(2, gap="large")

# ---- LEFT: LINE CHART ----
with col1:
    fig_line = px.line(
        df_filt,
        x=YEAR_COL, y=DEBT_COL,
        markers=True,
        title="External Debt Over Time (USD)",
        template="plotly_white"
    )
    fig_line.update_traces(line=dict(color=MAGENTA, width=3), marker=dict(color=MAGENTA, size=6))
    fig_line.update_layout(
        xaxis_title="Year",
        yaxis_title="External Debt (Current USD)",
        yaxis_type="log" if use_log_y else "linear",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=0),
    )
    fig_line.update_traces(hovertemplate="Year: %{x}<br>Debt: %{y:$,.0f}<extra></extra>")
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("**Analysis / Key takeaways**")
    st.write(LINE_ANALYSIS)
    st.markdown("**Why this graph?**")
    st.write(LINE_WHY)

# ---- RIGHT: SCATTER PLOT ----
with col2:
    # size encodes magnitude; cap size so it looks good
    size_range = [4, 16]
    fig_scatter = px.scatter(
        df_filt,
        x=YEAR_COL, y=DEBT_COL,
        color=DEBT_COL, size=DEBT_COL, size_max=size_range[1],
        title="Scatter of External Debt (USD)",
        template="plotly_white"
    )
    fig_scatter.update_layout(
        xaxis_title="Year",
        yaxis_title="External Debt (Current USD)",
        coloraxis_colorscale=COLORSCALE,
        margin=dict(l=10, r=10, t=50, b=0),
    )
    fig_scatter.update_traces(
        marker=dict(opacity=0.85, line=dict(width=0.5, color="white")),
        hovertemplate="Year: %{x}<br>Debt: %{y:$,.0f}<extra></extra>",
        selector=dict(mode="markers")
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("**Analysis / Key takeaways**")
    st.write(SCATTER_ANALYSIS)
    st.markdown("**Why this graph?**")
    st.write(SCATTER_WHY)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("If the app can't find your CSV, update the sidebar path to the exact file location in your repo (e.g., data/external_debt_dataset.csv).")
