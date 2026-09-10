import pandas as pd
import os

# ==========================================================
# BENGALURU BIKE SHARING DATASET - ETL PROCESS
# ==========================================================

# Create output folder
os.makedirs("Clean_Data", exist_ok=True)


# ==========================================================
# EXTRACT
# ==========================================================

print("=" * 60)
print("EXTRACT PHASE")
print("=" * 60)

input_file = "Raw_Data/Bengaluru_Bike_Sharing_Uncleaned_1000Rows.csv"

df = pd.read_csv(input_file)

print("Dataset loaded successfully!")
print("Original Rows:", len(df))
print("Original Columns:", len(df.columns))


# ==========================================================
# TRANSFORM
# ==========================================================

print("\n" + "=" * 60)
print("TRANSFORM PHASE")
print("=" * 60)


# 1. Remove completely empty rows
df.dropna(how="all", inplace=True)


# 2. Remove exact duplicate rows
duplicate_count = df.duplicated().sum()

print("Duplicate rows found:", duplicate_count)

df.drop_duplicates(inplace=True)

print("Rows after removing duplicates:", len(df))


# 3. Remove duplicate Trip_ID
before = len(df)

df.drop_duplicates(
    subset=["Trip_ID"],
    keep="first",
    inplace=True
)

print("Duplicate Trip_ID removed:", before - len(df))


# 4. Clean column names
df.columns = df.columns.str.strip()


# 5. Remove extra spaces from text columns
text_columns = df.select_dtypes(include="object").columns

for col in text_columns:
    df[col] = df[col].astype("string").str.strip()


# ==========================================================
# DATE AND TIME CLEANING
# ==========================================================

# Convert Date to proper datetime format
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)


# Convert Time to proper time format
df["Time"] = pd.to_datetime(
    df["Time"],
    format="%H:%M:%S",
    errors="coerce"
)


# Create Hour again from cleaned Time
df["Hour"] = df["Time"].dt.hour


# ==========================================================
# HANDLE MISSING TEXT VALUES
# ==========================================================

df["Station"] = df["Station"].fillna("Unknown")

df["Vehicle_Type"] = df["Vehicle_Type"].fillna("Unknown")

df["Peak_Demand"] = df["Peak_Demand"].fillna("Normal")


# ==========================================================
# VALIDATE NUMERIC VALUES
# ==========================================================

# Trip count cannot be negative
df.loc[
    df["Trip_Count"] < 0,
    "Trip_Count"
] = pd.NA


# Available bikes cannot be negative
df.loc[
    df["Available_Bikes"] < 0,
    "Available_Bikes"
] = pd.NA


# Total bikes cannot be zero or negative
df.loc[
    df["Total_Bikes"] <= 0,
    "Total_Bikes"
] = pd.NA


# Station utilisation must be between 0 and 100
df.loc[
    ~df["Station_Utilisation_Percentage"].between(0, 100),
    "Station_Utilisation_Percentage"
] = pd.NA


# Trip duration cannot be zero or negative
df.loc[
    df["Trip_Duration_min"] <= 0,
    "Trip_Duration_min"
] = pd.NA


# Validate Latitude
df.loc[
    ~df["Station_Latitude"].between(-90, 90),
    "Station_Latitude"
] = pd.NA


# Validate Longitude
df.loc[
    ~df["Station_Longitude"].between(-180, 180),
    "Station_Longitude"
] = pd.NA


# ==========================================================
# HANDLE MISSING NUMERIC VALUES
# ==========================================================

numeric_columns = [
    "Trip_Count",
    "Available_Bikes",
    "Total_Bikes",
    "Station_Utilisation_Percentage",
    "Trip_Duration_min",
    "Station_Latitude",
    "Station_Longitude"
]

for col in numeric_columns:
    df[col] = df[col].fillna(df[col].median())


# ==========================================================
# REMOVE RECORDS WITH CRITICAL MISSING DATA
# ==========================================================

df.dropna(
    subset=[
        "Trip_ID",
        "Date",
        "Time",
        "Station_ID",
        "Station"
    ],
    inplace=True
)


# ==========================================================
# RECALCULATE STATION UTILISATION
# ==========================================================

df["Station_Utilisation_Percentage"] = (
    df["Trip_Count"] / df["Total_Bikes"] * 100
).clip(0, 100).round(2)


# ==========================================================
# VALIDATE PEAK DEMAND
# ==========================================================

# Peak hours: morning and evening rush hours
peak_hours = [8, 9, 10, 17, 18, 19, 20]

df["Peak_Demand"] = df["Hour"].apply(
    lambda x: "Peak" if x in peak_hours else "Normal"
)


# ==========================================================
# SORT DATA
# ==========================================================

df.sort_values(
    by=["Date", "Time"],
    inplace=True
)


# Reset index
df.reset_index(
    drop=True,
    inplace=True
)


# ==========================================================
# FINAL DATA QUALITY CHECK
# ==========================================================

print("\n" + "=" * 60)
print("FINAL DATA QUALITY CHECK")
print("=" * 60)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Rows:", df.duplicated().sum())

print("\nFinal Rows:", len(df))
print("Final Columns:", len(df.columns))


# ==========================================================
# LOAD
# ==========================================================

print("\n" + "=" * 60)
print("LOAD PHASE")
print("=" * 60)

output_file = "Clean_Data/Bengaluru_Bike_Sharing_Clean.csv"

df.to_csv(
    output_file,
    index=False
)

print("Clean dataset saved successfully!")
print("Output File:", output_file)


# ==========================================================
# COMPLETION MESSAGE
# ==========================================================

print("\n" + "=" * 60)
print("ETL PROCESS COMPLETED SUCCESSFULLY!")
print("=" * 60)