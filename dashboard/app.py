import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Aadhaar Enrollment Gap Analysis",
    layout="wide"
)

st.title(" Aadhaar Enrollment & Update Gap Analysis")
st.markdown(
    """
    **Problem Statement:**  
    Identifying regional and age-based gaps in Aadhaar enrollment and update activity.
    """
)

district_df = pd.read_csv("outputs/reports/eda_district_level.csv")

st.sidebar.header("Filter")

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

if selected_state == "All":
    filtered_df = district_df.copy()
else:
    filtered_df = district_df[district_df["state"] == selected_state]

st.subheader(" Key Indicators")

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

st.subheader(" Update Composition (Child Age Group)")

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

total_updates = update_pie_df["Count"].sum()

if total_updates > 0:
    bio_pct = (update_pie_df.loc[
        update_pie_df["Type"] == "Biometric Updates", "Count"
    ].values[0] / total_updates) * 100

    demo_pct = 100 - bio_pct

    st.info(
        f" **Insight:** Biometric updates dominate Aadhaar maintenance for children "
        f"({bio_pct:.1f}% of total updates), indicating frequent biometric revalidation "
        f"due to physical growth. Demographic updates form only {demo_pct:.1f}%, "
        f"suggesting relatively stable personal information in this age group."
    )
else:
    st.warning("No update activity available to derive insights.")

st.divider()

st.subheader(" Districts with Highest Child Update Gap")

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

high_gap_districts = top_gap[top_gap["child_update_gap"] > 0]

if not high_gap_districts.empty:
    max_gap = high_gap_districts.iloc[0]

    st.info(
        f"**Insight:** Districts such as **{max_gap['district']}** exhibit a large "
        f"enrollment–update gap, where child enrollments significantly exceed update activity. "
        f"This indicates potential risks of outdated Aadhaar records and highlights the need "
        f"for targeted follow-up update campaigns in high-enrollment regions."
    )
else:
    st.info(
        " **Insight:** Child enrollment and update activity appear balanced across districts, "
        "indicating effective Aadhaar lifecycle maintenance."
    )

st.subheader(" District-Level Gap Intensity Heatmap")

heatmap_df = filtered_df.pivot_table(
    index="district",
    columns="state",
    values="child_update_gap",
    aggfunc="mean"
)

fig_heatmap = px.imshow(
    heatmap_df,
    color_continuous_scale="Reds",
    aspect="auto",
    height=700
)
st.plotly_chart(fig_heatmap, use_container_width=True)

abs_gap = heatmap_df.abs()

most_affected_state = abs_gap.sum(axis=0).idxmax()
most_affected_district = abs_gap.sum(axis=1).idxmax()

st.info(
    f" **Insight:** The update gap is spatially concentrated rather than uniform. "
    f"States such as **{most_affected_state}** exhibit multiple districts with high child "
    f"enrollment–update gaps, while districts like **{most_affected_district}** emerge as "
    f"persistent hotspots. This indicates localized Aadhaar maintenance challenges that "
    f"require targeted, district-level interventions."
)

st.divider()

st.subheader(" Treemap: Aadhaar Update Activity Contribution")

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

high_volume_df = treemap_df.sort_values("total_updates", ascending=False).head(10)

gap_heavy = high_volume_df[
    high_volume_df["child_update_gap"] > 0
]

if not gap_heavy.empty:
    top_district = gap_heavy.iloc[0]

    st.info(
        f" **Insight:** Aadhaar update activity is concentrated in high-volume districts such as "
        f"**{top_district['district']} ({top_district['state']})**, yet these districts still show "
        f"significant enrollment–update gaps. This suggests that update infrastructure has not "
        f"scaled proportionally with enrollment growth, highlighting the need for targeted capacity "
        f"expansion in high-load regions."
    )
else:
    st.info(
        " **Insight:** High-volume districts generally show balanced or update-heavy patterns, "
        "indicating effective scaling of Aadhaar update infrastructure."
    )

st.divider()

st.subheader("Enrollment by Age Group")

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

state_totals = age_df.groupby("state", as_index=False)["Count"].sum()
top_state = state_totals.sort_values("Count", ascending=False).iloc[0]["state"]

child_share_df = age_df.pivot(
    index="state",
    columns="Age Group",
    values="Count"
).fillna(0)

child_share_df["child_share_pct"] = (
    child_share_df["child_enrollment"] /
    (child_share_df["child_enrollment"] + child_share_df["adult_enrollment"])
) * 100

highest_child_share_state = (
    child_share_df.sort_values("child_share_pct", ascending=False)
    .index[0]
)

st.info(
    f"**Insight:** Adult enrollment accounts for the majority of Aadhaar coverage across "
    f"states, with **{top_state}** contributing the highest total enrollments. However, states "
    f"such as **{highest_child_share_state}** exhibit a relatively higher proportion of child "
    f"enrollments, indicating potential future pressure on Aadhaar update infrastructure as "
    f"these cohorts age."
)

update_heavy_df = filtered_df[filtered_df["child_update_gap"] < 0]

if not update_heavy_df.empty:
    top_update_heavy = (
        update_heavy_df
        .sort_values("child_update_gap")
        .iloc[0]
    )

    st.success(
        f"**Key Insight:** Update-heavy regions such as **{top_update_heavy['district']} "
        f"({top_update_heavy['state']})** indicate a higher Aadhaar lifecycle maintenance burden. "
        f"This is especially critical during child-to-adult transitions, where frequent biometric "
        f"and demographic updates are required to maintain data validity."
    )
else:
    st.success(
        " **Key Insight:** Most regions currently show enrollment-heavy patterns, indicating that "
        "future Aadhaar lifecycle maintenance demand is likely to increase as enrolled children age."
    )
