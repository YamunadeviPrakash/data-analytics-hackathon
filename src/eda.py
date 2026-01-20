import pandas as pd
import os

from cleaning import normalize_state_names

print("🚀 Starting EDA for Problem Statement 1")

DATA_PATH = "data/processed"
OUTPUT_PATH = "outputs/reports"

os.makedirs(OUTPUT_PATH, exist_ok=True)

# -------------------------------------------------
# Load datasets
# -------------------------------------------------
print("📥 Loading datasets...")

enrol = pd.read_csv(
    f"{DATA_PATH}/aadhaar_enrolment_cleaned.csv",
    low_memory=False
)
df = normalize_state_names(enrol)

demo = pd.read_csv(
    f"{DATA_PATH}/aadhaar_demographic_cleaned.csv",
    low_memory=False
)
df = normalize_state_names(demo)

bio = pd.read_csv(
    f"{DATA_PATH}/aadhaar_biometric_cleaned.csv",
    low_memory=False
)
df = normalize_state_names(bio)


print("✅ Datasets loaded")

# -------------------------------------------------
# Normalize column names
# -------------------------------------------------
enrol.columns = enrol.columns.str.lower().str.strip()
demo.columns = demo.columns.str.lower().str.strip()
bio.columns = bio.columns.str.lower().str.strip()

print("📌 Enrolment columns:", enrol.columns.tolist())
print("📌 Demographic columns:", demo.columns.tolist())
print("📌 Biometric columns:", bio.columns.tolist())

# -------------------------------------------------
# Validate required columns
# -------------------------------------------------
required_enrol = {"state", "district", "age_0_5", "age_5_17", "age_18_greater"}
required_demo = {"state", "district", "demo_age_5_17", "demo_age_17_"}
required_bio = {"state", "district", "bio_age_5_17", "bio_age_17_"}

assert required_enrol.issubset(enrol.columns), "❌ Missing columns in enrolment dataset"
assert required_demo.issubset(demo.columns), "❌ Missing columns in demographic dataset"
assert required_bio.issubset(bio.columns), "❌ Missing columns in biometric dataset"

print("✅ All required columns present")

GROUP_COLS = ["state", "district"]

# -------------------------------------------------
# Enrollment aggregation
# -------------------------------------------------
print("🔄 Aggregating enrollment data...")

enrollment = (
    enrol.groupby(GROUP_COLS, as_index=False)[
        ["age_0_5", "age_5_17", "age_18_greater"]
    ]
    .sum()
)

print("Enrollment rows:", len(enrollment))

# -------------------------------------------------
# Demographic updates aggregation
# -------------------------------------------------
print("🔄 Aggregating demographic updates...")

demo_updates = (
    demo.groupby(GROUP_COLS, as_index=False)[
        ["demo_age_5_17", "demo_age_17_"]
    ]
    .sum()
)

print("Demographic rows:", len(demo_updates))

# -------------------------------------------------
# Biometric updates aggregation
# -------------------------------------------------
print("🔄 Aggregating biometric updates...")

bio_updates = (
    bio.groupby(GROUP_COLS, as_index=False)[
        ["bio_age_5_17", "bio_age_17_"]
    ]
    .sum()
)

print("Biometric rows:", len(bio_updates))

# -------------------------------------------------
# Merge all datasets
# -------------------------------------------------
print("🔗 Merging datasets...")

merged = (
    enrollment
    .merge(demo_updates, on=GROUP_COLS, how="left")
    .merge(bio_updates, on=GROUP_COLS, how="left")
    .fillna(0)
)

print("Merged rows:", len(merged))

# -------------------------------------------------
# Gap analysis
# -------------------------------------------------
print("📊 Computing gap metrics...")

merged["child_update_gap"] = (
    merged["age_5_17"]
    - (merged["demo_age_5_17"] + merged["bio_age_5_17"])
)

merged["adult_update_gap"] = (
    merged["age_18_greater"]
    - (merged["demo_age_17_"] + merged["bio_age_17_"])
)

# -------------------------------------------------
# Transition Pressure Index
# -------------------------------------------------
merged["transition_pressure_index"] = (
    (merged["demo_age_17_"] + merged["bio_age_17_"])
    / merged["age_18_greater"].replace(0, 1)
)

# -------------------------------------------------
# Save district-level output
# -------------------------------------------------
district_file = f"{OUTPUT_PATH}/eda_district_level.csv"
merged.to_csv(district_file, index=False)

print(f"✅ District-level EDA saved → {district_file}")

# -------------------------------------------------
# State-level summary
# -------------------------------------------------
state_summary = (
    merged.groupby("state", as_index=False)
    .agg(
        total_child_enrollment=("age_5_17", "sum"),
        total_adult_enrollment=("age_18_greater", "sum"),
        avg_transition_pressure=("transition_pressure_index", "mean")
    )
)

state_file = f"{OUTPUT_PATH}/eda_state_level.csv"
state_summary.to_csv(state_file, index=False)

print(f"✅ State-level EDA saved → {state_file}")

print("🎉 EDA COMPLETED SUCCESSFULLY")
