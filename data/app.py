import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Plotly Insights", page_icon="📊", layout="wide")

st.title("📊 Plotly Visualizations with Context & Insights")
st.write(
    "This page presents two related visualizations from my previous Plotly assignment, "
    "with context and interesting insights."
)

# ---- Data loading ----
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

data_path = st.sidebar.text_input("Path to your CSV", "data/your_previous_plotly_data.csv")
try:
    df = load_data(data_path)
except Exception as e:
    st.error(f"Couldn't load data from '{data_path}'. Error: {e}")
    st.stop()

st.success(f"Loaded {len(df):,} rows.")
st.dataframe(df.head())

# ---- Column helpers ----
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
cat_cols = [c for c in df.columns if (df[c].dtype == "object" or pd.api.types.is_categorical_dtype(df[c]))]

with st.sidebar:
    st.header("Controls")
    st.caption("Pick columns that make sense for your dataset.")

    # Plot 1 (Scatter)
    st.subheader("Plot 1: Scatter")
    x_col = st.selectbox("X (numeric)", numeric_cols, index=0 if numeric_cols else None)
    y_col = st.selectbox("Y (numeric)", numeric_cols, index=1 if len(numeric_cols) > 1 else 0 if numeric_cols else None)
    color_col = st.selectbox("Color (categorical, optional)", [None] + cat_cols, index=0)

    # Plot 2 (Grouped metric by category)
    st.subheader("Plot 2: Grouped metric")
    group_col = st.selectbox("Group by (categorical)", cat_cols, index=0 if cat_cols else None)
    metric_col = st.selectbox("Metric (numeric to aggregate)", numeric_cols, index=0 if numeric_cols else None)
    agg_func = st.selectbox("Aggregation", ["mean", "sum", "median", "count"], index=0)

if not numeric_cols:
    st.warning("Your dataset needs at least one numeric column for these charts.")
    st.stop()
if not cat_cols:
    st.info("Plot 2 will work best if you have at least one categorical column.")

# ---- Layout ----
tab1, tab2 = st.tabs(["Scatter (Relationship)", "Grouped Metric (Comparison)"])

with tab1:
    st.subheader("Plot 1: Relationship between two numeric variables")
    if x_col and y_col:
        fig1 = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col if color_col else None,
            trendline=None,  # adds a regression line for insight
            height=500
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("### Context")
        st.write(
            f"- Exploring the relationship between **{x_col}** and **{y_col}**"
            + (f", colored by **{color_col}**." if color_col else ".")
        )
        st.markdown("### Insights (edit this text to match your findings)")
        st.write(
            "- Do you observe a positive/negative trend?\n"
            "- Any clusters by the chosen categorical variable?\n"
            "- Outliers that might need explanation or cleaning?"
        )

with tab2:
    st.subheader("Plot 2: Aggregated metric by category")
    if group_col and metric_col:
        # build summary
        if agg_func == "mean":
            summary = df.groupby(group_col, dropna=False)[metric_col].mean().reset_index()
        elif agg_func == "sum":
            summary = df.groupby(group_col, dropna=False)[metric_col].sum().reset_index()
        elif agg_func == "median":
            summary = df.groupby(group_col, dropna=False)[metric_col].median().reset_index()
        else:  # count
            summary = df.groupby(group_col, dropna=False)[metric_col].count().reset_index(name=metric_col)

        fig2 = px.bar(summary, x=group_col, y=metric_col, height=500)
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Context")
        st.write(
            f"- Comparing **{agg_func} {metric_col}** across **{group_col}** to see differences between groups."
        )
        st.markdown("### Insights (edit this text to match your findings)")
        st.write(
            "- Which group stands out as highest/lowest?\n"
            "- Any surprising differences compared to the scatter relationship?\n"
            "- Hypothesize reasons and next steps for analysis."
        )

st.markdown("---")
with st.expander("Methodology & Notes"):
    st.write(
        """
- Data source: briefly describe where your data came from.
- Cleaning steps: mention any filtering, imputation, or transformations.
- Why these two visuals are **related**: e.g., the scatter shows a relationship while the grouped bar compares the same metric across categories.
- Limitations: sample size, missing values, potential biases.
"""
    )
