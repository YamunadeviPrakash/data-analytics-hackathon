import zipfile
import pandas as pd
import os

RAW_DATA_PATH = "data/raw"
PROCESSED_DATA_PATH = "data/processed"

os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)


def unzip_and_merge(zip_filename, output_csv):
    zip_path = os.path.join(RAW_DATA_PATH, zip_filename)
    dfs = []

    print(f"\nProcessing: {zip_filename}")

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]

        print(f"Found {len(csv_files)} CSV files")

        for file in csv_files:
            with zip_ref.open(file) as csv_file:
                df = pd.read_csv(csv_file)
                dfs.append(df)

    merged_df = pd.concat(dfs, ignore_index=True)
    output_path = os.path.join(PROCESSED_DATA_PATH, output_csv)
    merged_df.to_csv(output_path, index=False)

    print(f"Saved merged file → {output_path}")
    print(f"Total rows: {len(merged_df)}")


if __name__ == "__main__":
    unzip_and_merge(
        "api_data_aadhar_biometric.zip",
        "aadhaar_biometric_merged.csv"
    )

    unzip_and_merge(
        "api_data_aadhar_demographic.zip",
        "aadhaar_demographic_merged.csv"
    )

    unzip_and_merge(
        "api_data_aadhar_enrolment.zip",
        "aadhaar_enrolment_merged.csv"
    )

    print("\nMerged all datasets")
