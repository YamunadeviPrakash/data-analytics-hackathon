import pandas as pd
import matplotlib.pyplot as plt
import os

from cleaning import normalize_state_names

from cleaning import normalize_state_names

# Paths
INPUT_PATH = "outputs/reports"
OUTPUT_PATH = "outputs/charts"

os.makedirs(OUTPUT_PATH, exist_ok=True)

print("📊 Starting visualization generation...")

# Load EDA outputs
district_df = pd.read_csv(f"{INPUT_PATH}/eda_district_level.csv")
district_df = normalize_state_names(district_df)

state_df = pd.read_csv(f"{INPUT_PATH}/eda_state_level.csv")
state_df = normalize_state_names(state_df)

print("✅ EDA files loaded")

# -------------------------------------------------
# 1️⃣ Child Enrollment vs Update Gap (Top 10 districts)
# -------------------------------------------------
top_child_gap = (
    district_df.sort_values("child_update_gap", ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 5))
plt.barh(
    top_child_gap["district"],
    top_child_gap["child_update_gap"]
)
plt.xlabel("Child Update Gap (Enrollments - Updates)")
plt.title("Top 10 Districts with Highest Child Update Gap")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}/child_update_gap.png")
plt.close()

print("✅ child_update_gap.png saved")

# -------------------------------------------------
# 2️⃣ Adult Enrollment vs Update Gap (Top 10 districts)
# -------------------------------------------------
top_adult_gap = (
    district_df.sort_values("adult_update_gap", ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 5))
plt.barh(
    top_adult_gap["district"],
    top_adult_gap["adult_update_gap"]
)
plt.xlabel("Adult Update Gap (Enrollments - Updates)")
plt.title("Top 10 Districts with Highest Adult Update Gap")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}/adult_update_gap.png")
plt.close()

print("✅ adult_update_gap.png saved")

# -------------------------------------------------
# 3️⃣ Transition Pressure Index (Top 10 districts)
# -------------------------------------------------
top_pressure = (
    district_df.sort_values(
        "transition_pressure_index", ascending=False
    )
    .head(10)
)

plt.figure(figsize=(10, 5))
plt.barh(
    top_pressure["district"],
    top_pressure["transition_pressure_index"]
)
plt.xlabel("Transition Pressure Index")
plt.title("Top 10 Districts Under Aadhaar Transition Pressure")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}/transition_pressure.png")
plt.close()

print("✅ transition_pressure.png saved")

# -------------------------------------------------
# 4️⃣ State-Level Overview (Child vs Adult Enrollment)
# -------------------------------------------------
plt.figure(figsize=(12, 6))
plt.bar(
    state_df["state"],
    state_df["total_child_enrollment"],
    label="Child Enrollment (5–17)"
)
plt.bar(
    state_df["state"],
    state_df["total_adult_enrollment"],
    bottom=state_df["total_child_enrollment"],
    label="Adult Enrollment (18+)"
)

plt.xticks(rotation=90)
plt.ylabel("Total Enrollment")
plt.title("State-wise Aadhaar Enrollment by Age Group")
plt.legend()
plt.tight_layout()
plt.savefig(f"{OUTPUT_PATH}/state_enrollment_overview.png")
plt.close()

print("✅ state_enrollment_overview.png saved")

print("🎉 All visualizations generated successfully")
