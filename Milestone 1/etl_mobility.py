import pandas as pd
import os

# ======================================================
# ETL PROCESS FOR BENGALURU MOBILITY DATASET
# ======================================================

# -----------------------------
# EXTRACT
# -----------------------------
print("=" * 50)
print("EXTRACT PHASE")
print("=" * 50)

# Read dataset
df = pd.read_csv(os.path.join("Raw_Data", "Mobility new.csv"))

print("Dataset Loaded Successfully")
print(f"Number of Rows    : {df.shape[0]}")
print(f"Number of Columns : {df.shape[1]}")
print()

# -----------------------------
# TRANSFORM
# -----------------------------
print("=" * 50)
print("TRANSFORM PHASE")
print("=" * 50)

# 1. Remove duplicate rows
duplicate_rows = df.duplicated().sum()
print("Duplicate Rows Before:", duplicate_rows)

df.drop_duplicates(inplace=True)

print("Duplicate Rows After :", df.duplicated().sum())
print()

# 2. Remove extra spaces from column names
df.columns = df.columns.str.strip()

# 3. Drop fully empty / junk columns
# "Unnamed: 7" is a completely blank column with no data in it at all -
# there's nothing meaningful to clean or fill, so it's dropped outright.
empty_columns = [col for col in df.columns if df[col].isnull().all()]
if empty_columns:
    print("Dropping fully empty columns:", empty_columns)
    df.drop(columns=empty_columns, inplace=True)
print()

# 4. Remove extra spaces from text columns
# NOTE: include both "object" and "string" - some pandas versions report
# text columns as dtype "str"/"string" instead of "object".
text_columns = df.select_dtypes(include=["object", "string"]).columns

for col in text_columns:
    df[col] = df[col].str.strip()

# 5. Convert Timestamp column to datetime EARLY, before the missing-value
# loop, so it's handled as a date rather than plain text.
df["Timestamp"] = pd.to_datetime(df["Timestamp"], format="%d-%m-%Y %H:%M", errors="coerce")

# 6. Check missing values
print("Missing Values Before Cleaning")
print(df.isnull().sum())
print()

# 7. Fill missing values
# NOTE: checking dtype == "object" is unreliable across pandas versions.
# Using pd.api.types helpers instead, and handling datetime separately.
for col in df.columns:

    if pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = df[col].ffill().bfill()

    elif pd.api.types.is_numeric_dtype(df[col]):
        df[col] = df[col].fillna(df[col].mean())

    else:
        df[col] = df[col].fillna("Unknown")

print("Missing Values After Cleaning")
print(df.isnull().sum())
print()

# 8. Remove negative values where negative doesn't make physical sense
# NOTE: Latitude/Longitude and Sentiment_Score are intentionally excluded -
# they are legitimately negative by design (NYC-area coordinates and a
# -1 to +1 sentiment scale). Blindly abs()-ing them would corrupt the data.
non_negative_columns = [
    "Vehicle_Count",
    "Traffic_Speed_kmh",
    "Road_Occupancy_%",
    "Accident_Report",
    "Ride_Sharing_Demand",
    "Parking_Availability",
    "Emission_Levels_g_km",
    "Energy_Consumption_L_h"
]

for col in non_negative_columns:
    if col in df.columns:
        df[col] = df[col].abs()

# 9. Clip percentage-based column to a valid 0-100 range
if "Road_Occupancy_%" in df.columns:
    df["Road_Occupancy_%"] = df["Road_Occupancy_%"].clip(lower=0, upper=100)

# 10. Clip Sentiment_Score to its valid -1 to 1 range
if "Sentiment_Score" in df.columns:
    df["Sentiment_Score"] = df["Sentiment_Score"].clip(lower=-1, upper=1)

# 11. Rename columns (Power BI friendly)
df.rename(columns={
    "Road_Occupancy_%": "Road_Occupancy_Pct"
}, inplace=True)

# 12. Sort data by Timestamp
df.sort_values(by="Timestamp", inplace=True)

# 13. Reset Index
df.reset_index(drop=True, inplace=True)

print("Final Dataset Shape:", df.shape)
print()

print("Data Types")
print(df.dtypes)
print()

# -----------------------------
# LOAD
# -----------------------------
print("=" * 50)
print("LOAD PHASE")
print("=" * 50)

# Create output folder
os.makedirs("Clean_Data", exist_ok=True)

output_file = "Clean_Data/Mobility_Clean.csv"

# Save cleaned dataset
df.to_csv(output_file, index=False)

print("Clean Dataset Saved Successfully")
print("Location :", output_file)
print()

print("=" * 50)
print("ETL PROCESS COMPLETED SUCCESSFULLY")
print("=" * 50)