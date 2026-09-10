import pandas as pd
import os

print("=" * 50)
print("EXTRACT PHASE")
print("=" * 50)

# Read dataset
df = pd.read_csv(os.path.join("Raw_Data", "Bengaluru_Demographic_Change.csv"))

print("Dataset Loaded Successfully")
print(f"Number of Rows    : {df.shape[0]}")
print(f"Number of Columns : {df.shape[1]}")
print()


# TRANSFORM

print("=" * 50)
print("TRANSFORM PHASE")
print("=" * 50)

#  Remove duplicate rows
duplicate_rows = df.duplicated().sum()
print("Duplicate Rows Before:", duplicate_rows)

df.drop_duplicates(inplace=True)

print("Duplicate Rows After :", df.duplicated().sum())
print()

# Remove extra spaces from column names
df.columns = df.columns.str.strip()

#  Remove extra spaces from text columns
text_columns = df.select_dtypes(include=["object", "string"]).columns

for col in text_columns:
    df[col] = df[col].str.strip()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

#  Check missing values
print("Missing Values Before Cleaning")
print(df.isnull().sum())
print()

#  Fill missing values

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

#  Rename columns (Power BI friendly)
df.rename(columns={
    "Area_sq_km": "Area_sq_km",
    "Young_Population_Rate": "Young_Population_Rate",
    "Adult_Population_Rate": "Adult_Population_Rate",
    "Older_Population_Rate": "Older_Population_Rate",
    "LiteracyRate": "Literacy_Rate",
    "GenderRatio": "Gender_Ratio",
    "MedianAge": "Median_Age",
    "EmploymentRate": "Employment_Rate"
}, inplace=True)

#  Remove negative values
numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns

for col in numeric_columns:
    df[col] = df[col].abs()

#  Remove invalid percentage values
percentage_columns = [
    "Young_Population_Rate",
    "Adult_Population_Rate",
    "Older_Population_Rate",
    "Literacy_Rate",
    "Employment_Rate"
]

for col in percentage_columns:
    df[col] = df[col].clip(lower=0, upper=100)

# . Create Population Density
df["Population_Density"] = (
    df["Population"] / df["Area_sq_km"]
).round(2)

# 11. Sort data by Date
df.sort_values(by="Date", inplace=True)

# 12. Reset Index
df.reset_index(drop=True, inplace=True)

print("Final Dataset Shape:", df.shape)
print()

print("Data Types")
print(df.dtypes)
print()


print(df.mean(numeric_only=True))

#LOAD
print("=" * 50)
print("LOAD PHASE")
print("=" * 50)

# Create output folder
os.makedirs("Clean_Data", exist_ok=True)

output_file = "Clean_Data/Bengaluru_Demographic_Clean.csv"

# Save cleaned dataset
df.to_csv(output_file, index=False)

print("Clean Dataset Saved Successfully")
print("Location :", output_file)
print()

print("=" * 50)
print("ETL PROCESS COMPLETED SUCCESSFULLY")
print("=" * 50)