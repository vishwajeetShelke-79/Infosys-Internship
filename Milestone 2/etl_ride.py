import pandas as pd
import os

# ==========================================================
# BENGALURU RIDE-HAILING DATASET ETL
# ==========================================================

# Create output folder
os.makedirs("Clean_Data", exist_ok=True)


# ==========================================================
# EXTRACT
# ==========================================================

print("=" * 60)
print("EXTRACT PHASE")
print("=" * 60)

input_file = "Raw_Data/Bengaluru_Ride_Hailing_Uncleaned_1000Rows.csv"

df = pd.read_csv(input_file)

print("Dataset loaded successfully")
print("Original Rows    :", len(df))
print("Original Columns :", len(df.columns))


# ==========================================================
# TRANSFORM
# ==========================================================

print("\n" + "=" * 60)
print("TRANSFORM PHASE")
print("=" * 60)


# 1. Remove completely empty rows

df.dropna(how="all", inplace=True)


# 2. Remove duplicate rows

duplicate_count = df.duplicated().sum()

print("Duplicate rows found:", duplicate_count)

df.drop_duplicates(inplace=True)

print("Duplicate rows after cleaning:", df.duplicated().sum())


# 3. Clean column names

df.columns = df.columns.str.strip()


# 4. Remove extra spaces from text columns

text_columns = df.select_dtypes(include="object").columns

for col in text_columns:
    df[col] = df[col].str.strip()


# ==========================================================
# 5. CONVERT DATE AND TIME
# ==========================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df["Time"] = pd.to_datetime(
    df["Time"],
    format="%H:%M:%S",
    errors="coerce"
).dt.time


# ==========================================================
# 6. HANDLE MISSING LOCATION
# ==========================================================

df["Location"] = df["Location"].fillna("Unknown")


# ==========================================================
# 7. CHECK INVALID NUMERIC VALUES
# ==========================================================

# Ride requests cannot be negative

df.loc[
    df["Ride_Request"] < 0,
    "Ride_Request"
] = pd.NA


# Available vehicles cannot be negative

df.loc[
    df["Available_Vehicles"] < 0,
    "Available_Vehicles"
] = pd.NA


# Completed rides cannot be negative

df.loc[
    df["Completed_Ride"] < 0,
    "Completed_Ride"
] = pd.NA


# Cancelled rides cannot be negative

df.loc[
    df["Cancel_Ride"] < 0,
    "Cancel_Ride"
] = pd.NA


# Waiting time cannot be negative

df.loc[
    df["Waiting_Time_min"] < 0,
    "Waiting_Time_min"
] = pd.NA


# Surge multiplier should be at least 1

df.loc[
    df["Surge_Multiplier"] < 1,
    "Surge_Multiplier"
] = pd.NA


# ==========================================================
# 8. HANDLE MISSING NUMERIC VALUES
# ==========================================================

numeric_columns = [
    "Ride_Request",
    "Available_Vehicles",
    "Completed_Ride",
    "Cancel_Ride",
    "Waiting_Time_min",
    "Surge_Multiplier"
]

for col in numeric_columns:

    df[col] = df[col].fillna(
        df[col].median()
    )


# ==========================================================
# 9. REMOVE ROWS WITH INVALID DATE
# ==========================================================

df.dropna(
    subset=["Date"],
    inplace=True
)


# ==========================================================
# 10. VALIDATE RIDE COUNTS
# ==========================================================

# Completed rides + cancelled rides
# should not normally exceed ride requests.

invalid_rides = (
    df["Completed_Ride"] +
    df["Cancel_Ride"]
) > df["Ride_Request"]

print(
    "Invalid ride-count records:",
    invalid_rides.sum()
)

# Correct invalid records by limiting completed rides
# to the number of ride requests.

df.loc[
    invalid_rides,
    "Completed_Ride"
] = df.loc[
    invalid_rides,
    "Ride_Request"
]

# Recalculate cancelled rides

df["Cancel_Ride"] = (
    df["Ride_Request"] -
    df["Completed_Ride"]
)


# ==========================================================
# 11. ROUND DECIMAL VALUES
# ==========================================================

df["Waiting_Time_min"] = df[
    "Waiting_Time_min"
].round(2)

df["Surge_Multiplier"] = df[
    "Surge_Multiplier"
].round(2)


# ==========================================================
# 12. SORT DATA
# ==========================================================

df.sort_values(
    by=["Date", "Time"],
    inplace=True
)


# ==========================================================
# 13. RESET INDEX
# ==========================================================

df.reset_index(
    drop=True,
    inplace=True
)


# ==========================================================
# 14. FINAL DATA QUALITY CHECK
# ==========================================================

print("\nFinal Missing Values:")
print(df.isnull().sum())

print("\nFinal Dataset Shape:")
print(df.shape)


# ==========================================================
# LOAD
# ==========================================================

print("\n" + "=" * 60)
print("LOAD PHASE")
print("=" * 60)

output_file = (
    "Clean_Data/"
    "Bengaluru_Ride_Hailing_Clean.csv"
)

df.to_csv(
    output_file,
    index=False
)

print("Clean dataset saved successfully!")
print("Output:", output_file)


# ==========================================================
# COMPLETION MESSAGE
# ==========================================================

print("\n" + "=" * 60)
print("ETL PROCESS COMPLETED SUCCESSFULLY")
print("=" * 60)