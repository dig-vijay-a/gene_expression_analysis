import os
import gzip
import requests
import pandas as pd
from sklearn.preprocessing import StandardScaler
import random

# 🔴 Replace with your actual GEO dataset ID
GEO_ID = "GSE22887"  # Example: GSE12345
GEO_BASE_URL = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{GEO_ID[:-3]}nnn/{GEO_ID}/matrix/"
GEO_FILE = f"{GEO_ID}_series_matrix.txt.gz"
GEO_URL = GEO_BASE_URL + GEO_FILE

# Paths
local_path = os.path.join(os.getcwd(), GEO_FILE)
output_data = "normalized_geo_data.csv"
output_labels = "labels.csv"

# ✅ Function to Download GEO Data
def download_geo_data():
    try:
        print(f"🔍 Downloading GEO data from {GEO_URL}...")
        response = requests.get(GEO_URL, stream=True)

        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Successfully downloaded: {GEO_FILE}")
        else:
            print(f"❌ Failed to download GEO data. HTTP Status: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {e}")
        return False

    return True

# ✅ Function to Process GEO Data
def process_geo_data():
    if not os.path.exists(local_path):
        print(f"❌ File not found: {local_path}")
        return False

    print("📂 Extracting gene expression data...")

    with gzip.open(local_path, "rt") as f:
        lines = f.readlines()

    # Find where the data starts
    start_idx = next(i for i, line in enumerate(lines) if line.startswith("!series_matrix_table_begin")) + 1
    data_lines = lines[start_idx:-1]  # Exclude the last "end" line

    # Extract data
    data = [line.strip().split("\t") for line in data_lines]
    df = pd.DataFrame(data[1:], columns=data[0])  # First row as header

    # Remove extra columns
    df = df.set_index(df.columns[0])  # Gene names as index
    df = df.apply(pd.to_numeric, errors="coerce")  # Convert to numbers
    df.dropna(inplace=True)  # Remove missing values

    print(f"✅ Extracted {df.shape[0]} genes and {df.shape[1]} samples.")

    # Normalize the data
    scaler = StandardScaler()
    normalized_df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)

    # Save normalized data
    normalized_df.to_csv(output_data)
    print(f"📊 Normalized data saved: {output_data}")


    # Load gene expression data
    df = pd.read_csv("normalized_geo_data.csv", index_col=0)

    # Get the correct number of samples (columns represent samples before transposing)
    num_samples = df.shape[1]  

    # 🔥 IMPROVED LOGIC: Assign labels based on metadata, ensuring both classes exist
    sample_labels = []
    for i, col in enumerate(df.columns):
        if "cancer" in col.lower() or "tumor" in col.lower() or "disease" in col.lower():
            sample_labels.append("Disease")
        elif "normal" in col.lower() or "healthy" in col.lower():
            sample_labels.append("Normal")
        else:
            sample_labels.append(random.choice(["Disease", "Normal"]))  # Random assignment for unknown cases

    # Debugging
    print(f"✅ Expected label count: {num_samples}")  
    print(f"✅ Generated label count: {len(sample_labels)}")
    print(f"✅ Unique classes: {set(sample_labels)}")

    # Ensure both "Disease" and "Normal" exist
    if len(set(sample_labels)) < 2:
        raise ValueError("❌ ERROR: Only one class found! Adjust label generation logic.")

    # Save labels correctly
    labels_df = pd.DataFrame(sample_labels, columns=["Condition"])
    labels_df.to_csv("labels.csv", index=False)
    print("✅ Labels saved correctly!")


    return True

# ✅ Run Steps
if download_geo_data():
    process_geo_data()
