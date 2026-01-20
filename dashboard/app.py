import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# Page setup
# -------------------------------------------------
st.set_page_config(
    page_title="Aadhaar Enrollment Gap Analysis",
    layout="wide"
)

st.title("🆔 Aadhaar Enrollment & Update Gap Analysis")
st.markdown(
    """
    **Problem Statement:**  
    Identifying regional and age-based gaps in Aadhaar enrollment and update activity.
    """
)

# -------------------------------------------------
# Load data
# -------------------------------------------------
district_df = pd.read_csv("outputs/reports/eda_district_level.csv")

# -------------------------------------------------
# Sidebar Filter (WORKING & FINAL)
# -------------------------------------------------
st.sidebar.header("🔎 Filter")

states = (
    district_df["state"]
    .astype(str)
    .str.strip()
)

states = states[states.str.contains(r"[A-Za-z]", regex=True)]
states = sorted(states.unique())

selected_state = st.sidebar.selectbox(
    "Select State",
    options=["All"] + states
)

# -------------------------------------------------
# Filtered dataframe (SINGLE SOURCE OF TRUTH)
# -------------------------------------------------
if selected_state == "All":
    filtered_df = district_df.copy()
else:
    filtered_df = district_df[district_df["state"] == selected_state]

# -------------------------------------------------
# KPI Section (FIXED)
# -------------------------------------------------
st.subheader("📌 Key Indicators")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Child Enrollment (5–17)",
    int(filtered_df["age_5_17"].sum())
)

c2.metric(
    "Total Demographic Updates (5–17)",
    int(filtered_df["demo_age_5_17"].sum())
)

c3.metric(
    "Avg Transition Pressure Index",
    round(filtered_df["transition_pressure_index"].mean(), 2)
)

st.divider()

# =================================================
# 1️⃣ PIE — UPDATE COMPOSITION (FIXED)
# =================================================
st.subheader("🟠 Update Composition (Child Age Group)")

update_pie_df = pd.DataFrame({
    "Type": ["Demographic Updates", "Biometric Updates"],
    "Count": [
        filtered_df["demo_age_5_17"].sum(),
        filtered_df["bio_age_5_17"].sum()
    ]
})

fig_pie = px.pie(
    update_pie_df,
    names="Type",
    values="Count",
    hole=0.45,
    height=450
)

st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# =================================================
# 2️⃣ BAR — TOP UPDATE GAPS (FIXED)
# =================================================
st.subheader("📊 Districts with Highest Child Update Gap")

top_gap = (
    filtered_df
    .sort_values("child_update_gap", ascending=False)
    .head(15)
)

fig_bar = px.bar(
    top_gap,
    x="child_update_gap",
    y="district",
    orientation="h",
    height=600,
    labels={
        "child_update_gap": "Enrollment Surplus (+) / Update Surplus (−)"
    }
)

fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})

st.plotly_chart(fig_bar, use_container_width=True)

st.caption(
    "Positive values indicate enrollment-heavy regions (coverage gaps). "
    "Negative values indicate update-heavy regions (maintenance burden)."
)

st.divider()

# =================================================
# 3️⃣ HEATMAP — GAP INTENSITY (FIXED)
# =================================================
st.subheader("🔥 District-Level Gap Intensity Heatmap")

heatmap_df = filtered_df.pivot_table(
    index="district",
    columns="state",
    values="child_update_gap",
    aggfunc="sum"
)

fig_heatmap = px.imshow(
    heatmap_df,
    color_continuous_scale="Reds",
    aspect="auto",
    height=700
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.divider()

# =================================================
# 4️⃣ TREEMAP — UPDATE ACTIVITY CONTRIBUTION (FIXED)
# =================================================
st.subheader("🌳 Treemap: Aadhaar Update Activity Contribution")

filtered_df = filtered_df.copy()
filtered_df["total_updates"] = (
    filtered_df["demo_age_5_17"].fillna(0) +
    filtered_df["bio_age_5_17"].fillna(0)
)

treemap_df = filtered_df[filtered_df["total_updates"] > 0]

if treemap_df.empty:
    st.warning("No update activity available for treemap visualization.")
else:
    fig_tree = px.treemap(
        treemap_df,
        path=["state", "district"],
        values="total_updates",
        color="child_update_gap",
        color_continuous_scale="RdYlGn_r",
        height=700
    )
    st.plotly_chart(fig_tree, use_container_width=True)

st.divider()

# =================================================
# 5️⃣ STACKED BAR — AGE COMPARISON (FIXED)
# =================================================
st.subheader("📈 Enrollment by Age Group")

age_df = filtered_df.groupby("state", as_index=False).agg(
    child_enrollment=("age_5_17", "sum"),
    adult_enrollment=("age_18_greater", "sum")
)

age_df = age_df.melt(
    id_vars="state",
    value_vars=["child_enrollment", "adult_enrollment"],
    var_name="Age Group",
    value_name="Count"
)

fig_stack = px.bar(
    age_df,
    x="state",
    y="Count",
    color="Age Group",
    barmode="stack",
    height=600
)

st.plotly_chart(fig_stack, use_container_width=True)

# -------------------------------------------------
# Final Insight
# -------------------------------------------------
st.success(
    "📌 Key Insight: Regions with high update-heavy patterns indicate "
    "greater Aadhaar lifecycle maintenance burden, especially during "
    "child-to-adult transitions."
)
