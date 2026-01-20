import pandas as pd
import os

INPUT_PATH = "data/processed"
OUTPUT_PATH = "data/processed"

os.makedirs(OUTPUT_PATH, exist_ok=True)


def clean_dataset(input_file, output_file):
    print(f"\nCleaning: {input_file}")

    file_path = os.path.join(INPUT_PATH, input_file)
    df = pd.read_csv(file_path)
    df = normalize_state_names(df)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].fillna("Unknown")
        else:
            df[col] = df[col].fillna(0)

    for col in df.columns:
        if "date" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df = df.dropna(how="all")

    output_file_path = os.path.join(OUTPUT_PATH, output_file)
    df.to_csv(output_file_path, index=False)

    print(f"Saved cleaned file → {output_file_path}")
    print(f"Final shape: {df.shape}")

def normalize_state_names(df):
    
    df = df[df["state"].astype(str).str.contains(r"[a-zA-Z]", regex=True)]
    df["state"] = (
        df["state"]
        .str.lower()
        .str.strip()
        .str.replace("&", "and")
        .str.replace(r"\s+", " ", regex=True)
    )

    state_mapping = {

    "jammu and kashmir": "Jammu and Kashmir",
    "jammu kashmir": "Jammu and Kashmir",

    "the dadra and nagar haveli and daman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "dadra and nagar haveli and daman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "daman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "damman and diu": "Dadra And Nagar Haveli And Daman And Diu",
    "dadra and nagar haveli": "Dadra And Nagar Haveli And Daman And Diu",

    "west bengal": "West Bengal",
    "west bangal": "West Bengal",
    "westbengal": "West Bengal",
    "w bengal": "West Bengal",
    "w. bengal": "West Bengal",
    "wb": "West Bengal",

    "orissa": "Odisha",

    "pondicherry": "Puducherry",

    "telengana": "Telangana"
    }

    df["state"] = df["state"].replace(state_mapping)
    df["state"] = df["state"].str.title()
    df["state"] = (
    df["state"]
    .str.lower()
    .str.replace("&", "and")
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
    )
    df["state"] = df["state"].replace(state_mapping)
    df["state"] = df["state"].str.title()

    return df

if __name__ == "__main__":
    clean_dataset(
        "aadhaar_biometric_merged.csv",
        "aadhaar_biometric_cleaned.csv"
    )

    clean_dataset(
        "aadhaar_demographic_merged.csv",
        "aadhaar_demographic_cleaned.csv"
    )

    clean_dataset(
        "aadhaar_enrolment_merged.csv",
        "aadhaar_enrolment_cleaned.csv"
    )

    print("\nData cleaning completed")
