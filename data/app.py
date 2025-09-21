import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Lebanon External Debt", page_icon="📈", layout="wide")

# ===== Sidebar: data path & basic controls =====
st.sidebar.header("Data")
data_path = st.sidebar.text_input("Path to your CSV", "data/your_file_name.csv")
st.sidebar.caption("Example: data/lebanon_external_debt.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize headers & drop any accidental index columns
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]
    # expected columns based on your notebook
    rename_map = {"refPeriod": "Year", "Value": "External_Debt"}
    for k, v in rename_map.items():
        if k in df.columns and v not in df.columns:
            df = df.rename(columns={k: v})
    # enforce types if possible
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    if "External_Debt" in df.columns:
        df["External_Debt"] = pd.to_numeric(df["External_Debt"], errors="coerce")
    df = df.dropna(subset=["Year", "External_Debt"])
    return df.sort_values("Year")

try:
    df = load_data(data_path)
except Exception as e:
    st.error(f"Couldn't load data from '{data_path}'. Error: {e}")
    st.stop()

st.success(f"Loaded {len(df):,} rows from {data_path}")
with st.expander("Preview data", expanded=False):
    st.dataframe(df.head())

# ===== Sidebar: filters & options =====
st.sidebar.header("Filters")
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider("Year range", min_year, max_year, (min_year, max_year), step=1)
df_range = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])].copy()

st.sidebar.header("Line options")
show_ma = st.sidebar.checkbox("Show moving average", value=True)
ma_window = st.sidebar.slider("MA window (years)", 3, 15, 5, step=1, disabled=not show_ma)
use_log_y = st.sidebar.checkbox("Log scale (Y)", value=False)

st.sidebar.header("Scatter options")
show_trend = st.sidebar.checkbox("Add LOWESS-like smoother (visual only)", value=False)
# (We’ll emulate with rolling mean visually; no extra package needed.)

# ===== Helper: nice number formatting =====
def billions(x):
    try:
        return f"{x/1e9:.1f}B"
    except Exception:
        return x

# ===== Tabs =====
tab1, tab2 = st.tabs(["📈 Line: External Debt Over Time", "🟣 Scatter: Year vs External Debt"])

# ===== Tab 1: LINE =====
with tab1:
    # your magenta brand
    MAGENTA = "#a429aa"  # from your assignment
    title = "Lebanon External Debt Over Time (USD)"
    fig_line = px.line(
        df_range,
        x="Year",
        y="External_Debt",
        markers=True,
        title=title,
        template="plotly_white",
    )
    fig_line.update_traces(line=dict(color=MAGENTA), marker=dict(color=MAGENTA, size=6))
    fig_line.update_layout(
        xaxis_title="Year",
        yaxis_title="External Debt (Current USD)",
        yaxis_type="log" if use_log_y else "linear",
        hovermode="x unified",
    )
    # optional moving average
    if show_ma and len(df_range) >= ma_window:
        df_range["MA"] = df_range["External_Debt"].rolling(ma_window, center=True).mean()
        fig_line.add_scatter(
            x=df_range["Year"],
            y=df_range["MA"],
            mode="lines",
            name=f"{ma_window}-yr MA",
            line=dict(width=3, dash="solid", color="#6e1a70"),
        )

    # pretty hovers
    fig_line.update_traces(
        hovertemplate="Year: %{x}<br>Debt: %{y:$,.0f}<extra></extra>"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # quick insight box to edit later
    st.markdown("### Notes & Insights")
    st.write(
        "- Use the **Year range** slider to zoom.\n"
        "- Toggle **Log scale** to inspect earlier decades.\n"
        "- The **moving average** line smooths volatility."
    )

# ===== Tab 2: SCATTER =====
with tab2:
    # your custom magenta → turquoise gradient
    custom_scale = [
        (0.00, "#a429aa"),
        (0.25, "#c868c9"),
        (0.50, "#e8c6e9"),
        (0.75, "#66d7d1"),
        (1.00, "#11c7c7"),
    ]
    fig_scatter = px.scatter(
        df_range,
        x="Year",
        y="External_Debt",
        color="External_Debt",
        template="plotly_white",
        title="Scatter of Lebanon External Debt (USD)",
    )
    fig_scatter.update_layout(
        xaxis_title="Year",
        yaxis_title="External Debt (Current USD)",
        coloraxis_colorscale=custom_scale,
    )
    fig_scatter.update_traces(
        marker=dict(opacity=0.8, line=dict(width=0.5, color="white")),
        hovertemplate="Year: %{x}<br>Debt: %{y:$,.0f}<extra></extra>",
    )

    # visual smoother (rolling median on y)
    if show_trend and len(df_range) >= 5:
        df_tr = df_range[["Year", "External_Debt"]].copy()
        df_tr["Smooth"] = df_tr["External_Debt"].rolling(7, center=True).median()
        fig_scatter.add_traces(
            px.line(df_tr, x="Year", y="Smooth").update_traces(
                name="Smooth (rolling median)",
                line=dict(width=3, color="#2a9da0"),
                hovertemplate="Year: %{x}<br>Smooth: %{y:$,.0f}<extra></extra>",
            ).data
        )

    st.plotly_chart(fig_scatter, use_container_width=True)

# ===== Footer =====
st.markdown("---")
st.caption("Tip: If the app says it can't find your CSV, update the sidebar path to the exact file location in your repo.")
