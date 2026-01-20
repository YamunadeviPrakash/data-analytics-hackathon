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
state_df = pd.read_csv("outputs/reports/eda_state_level.csv")

# -------------------------------------------------
# Sidebar filter (DEDUPLICATED & SORTED)
# -------------------------------------------------
st.sidebar.header("🔎 Filter")

states = (
    district_df["state"]
    .astype(str)
    .str.strip()
)

# 🚨 Remove numeric / invalid entries
states = states[states.str.contains(r"[A-Za-z]", regex=True)]

states = sorted(states.unique())

selected_state = st.sidebar.selectbox(
    "Select State",
    options=["All"] + states
)

# -------------------------------------------------
# KPI Section
# -------------------------------------------------
st.subheader("📌 Key Indicators")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Total Child Enrollment (5–17)",
    int(district_df["age_5_17"].sum())
)

c2.metric(
    "Total Demographic Updates (5–17)",
    int(district_df["demo_age_5_17"].sum())
)

c3.metric(
    "Avg Transition Pressure Index",
    round(district_df["transition_pressure_index"].mean(), 2)
)

st.divider()

# =================================================
# 1️⃣ PIE — UPDATE COMPOSITION (FIXED LOGIC)
# =================================================
st.subheader("🟠 Update Composition (Child Age Group)")

st.markdown(
    """
    **Why this Pie Chart?**  
    Pie charts should represent **parts of a whole**.  
    Here, we show how **demographic vs biometric updates**
    contribute to total update activity.
    """
)

update_pie_df = pd.DataFrame({
    "Type": ["Demographic Updates", "Biometric Updates"],
    "Count": [
        district_df["demo_age_5_17"].sum(),
        district_df["bio_age_5_17"].sum()
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
# 2️⃣ BAR — TOP UPDATE GAPS
# =================================================
st.subheader("📊 Districts with Highest Child Update Gap")

st.markdown(
    """
    **Why Bar Chart?**  
    Best for **ranking regions** and identifying worst-affected districts.
    """
)

top_gap = (
    district_df.sort_values("child_update_gap", ascending=False)
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
    },
    title="Districts by Enrollment vs Update Balance (Age 5–17)"
)
st.caption(
    "Positive values indicate enrollment-heavy regions (potential coverage gaps). "
    "Negative values indicate update-heavy regions (higher Aadhaar maintenance burden)."
)

fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})

st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# =================================================
# 3️⃣ HEATMAP — GAP INTENSITY (FIXED SCALE)
# =================================================
st.subheader("🔥 District-Level Gap Intensity Heatmap")

st.markdown(
    """
    **Why Heatmap?**  
    Heatmaps reveal **concentration and hotspots**
    across regions at a glance.
    """
)

heatmap_df = district_df.pivot_table(
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

st.markdown(
    """
    **Why Treemap?**  
    Treemaps show **hierarchical contribution**.
    
    • **Size** → total update activity  
    • **Color** → severity of enrollment–update gap  
    """
)

# Compute total updates safely
district_df["total_updates"] = (
    district_df["demo_age_5_17"].fillna(0) +
    district_df["bio_age_5_17"].fillna(0)
)

# 🚨 CRITICAL FIX: remove zero-weight rows
treemap_df = district_df[district_df["total_updates"] > 0]

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

# =================================================
# 5️⃣ STACKED BAR — AGE COMPARISON
# =================================================
st.subheader("📈 State-wise Enrollment by Age Group")

st.markdown(
    """
    **Why Stacked Bar?**  
    Shows **age-wise composition** while preserving total enrollment.
    """
)

age_df = state_df.melt(
    id_vars="state",
    value_vars=["total_child_enrollment", "total_adult_enrollment"],
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
    "📌 Key Insight: Several districts show high enrollment but "
    "disproportionately low update activity, indicating potential risks "
    "to Aadhaar data validity during age transitions."
)