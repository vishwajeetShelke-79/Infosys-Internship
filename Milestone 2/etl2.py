import pandas as pd
import os

# ==========================================================
# CREATE OUTPUT FOLDER
# ==========================================================

os.makedirs("Clean_Data", exist_ok=True)


# ==========================================================
# FUNCTION FOR GEOSPATIAL DATASET
# ==========================================================

def clean_geospatial():

    print("\n")
    print("=" * 60)
    print("GEOSPATIAL DATASET ETL")
    print("=" * 60)

    # ------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------

    input_file = "Raw_Data/Bengaluru_Geospatial_Uncleaned.csv"

    df = pd.read_csv(input_file)

    print("\nEXTRACT")
    print("-" * 40)
    print("Original Rows    :", len(df))
    print("Original Columns :", len(df.columns))


    # ------------------------------------------------------
    # TRANSFORM
    # ------------------------------------------------------

    print("\nTRANSFORM")
    print("-" * 40)

    # 1. Remove completely empty rows
    df.dropna(how="all", inplace=True)

    # 2. Remove duplicate records
    before = len(df)

    df.drop_duplicates(inplace=True)

    print("Duplicate rows removed:", before - len(df))


    # 3. Remove duplicate GeoID
    before = len(df)

    df.drop_duplicates(
        subset=["GeoID"],
        keep="first",
        inplace=True
    )

    print("Duplicate GeoID removed:", before - len(df))


    # 4. Remove spaces from column names
    df.columns = df.columns.str.strip()


    # 5. Remove spaces from text columns
    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()


    # 6. Convert Date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    # 7. Handle missing City
    df["City"] = df["City"].fillna("Bengaluru")


    # 8. Handle missing Ward
    df["Ward"] = df["Ward"].fillna("Unknown")


    # 9. Handle missing Land Use
    df["Land_Use"] = df["Land_Use"].replace(
        "", pd.NA
    )

    df["Land_Use"] = df["Land_Use"].fillna(
        "Unknown"
    )


    # ------------------------------------------------------
    # VALIDATE NUMERIC VALUES
    # ------------------------------------------------------

    # Latitude should be within valid geographic range
    df.loc[
        ~df["Latitude"].between(-90, 90),
        "Latitude"
    ] = pd.NA


    # Longitude should be within valid geographic range
    df.loc[
        ~df["Longitude"].between(-180, 180),
        "Longitude"
    ] = pd.NA


    # Area cannot be zero or negative
    df.loc[
        df["Area_sq_km"] <= 0,
        "Area_sq_km"
    ] = pd.NA


    # Green cover must be between 0 and 100
    df.loc[
        ~df["Green_Cover_Percentage"].between(0, 100),
        "Green_Cover_Percentage"
    ] = pd.NA


    # Road density cannot be negative
    df.loc[
        df["Road_Density_km_per_sq_km"] < 0,
        "Road_Density_km_per_sq_km"
    ] = pd.NA


    # Distance cannot be negative
    df.loc[
        df["Distance_to_City_Center_km"] < 0,
        "Distance_to_City_Center_km"
    ] = pd.NA


    # ------------------------------------------------------
    # REMOVE ROWS WITH INVALID CRITICAL DATA
    # ------------------------------------------------------

    df.dropna(
        subset=[
            "GeoID",
            "Date",
            "Ward",
            "Latitude",
            "Longitude",
            "Area_sq_km"
        ],
        inplace=True
    )


    # ------------------------------------------------------
    # FILL REMAINING NUMERIC MISSING VALUES
    # ------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    for col in numeric_columns:

        df[col] = df[col].fillna(
            df[col].median()
        )


    # ------------------------------------------------------
    # SORT DATA
    # ------------------------------------------------------

    df.sort_values(
        by="Date",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )


    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    output_file = (
        "Clean_Data/"
        "Bengaluru_Geospatial_Clean.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )


    print("\nLOAD")
    print("-" * 40)
    print("Final Rows:", len(df))
    print("Clean file:", output_file)

    return df


# ==========================================================
# FUNCTION FOR TRANSIT DATASET
# ==========================================================

def clean_transit():

    print("\n")
    print("=" * 60)
    print("TRANSIT DATASET ETL")
    print("=" * 60)

    # ------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------

    input_file = (
        "Raw_Data/"
        "Bengaluru_Transit_Uncleaned.csv"
    )

    df = pd.read_csv(input_file)

    print("\nEXTRACT")
    print("-" * 40)
    print("Original Rows    :", len(df))
    print("Original Columns :", len(df.columns))


    # ------------------------------------------------------
    # TRANSFORM
    # ------------------------------------------------------

    print("\nTRANSFORM")
    print("-" * 40)

    # 1. Remove completely empty rows
    df.dropna(
        how="all",
        inplace=True
    )


    # 2. Remove duplicate records
    before = len(df)

    df.drop_duplicates(
        inplace=True
    )

    print(
        "Duplicate rows removed:",
        before - len(df)
    )


    # 3. Remove duplicate TransitID
    before = len(df)

    df.drop_duplicates(
        subset=["TransitID"],
        keep="first",
        inplace=True
    )

    print(
        "Duplicate TransitID removed:",
        before - len(df)
    )


    # 4. Clean column names
    df.columns = df.columns.str.strip()


    # 5. Clean text columns
    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for col in text_columns:

        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )


    # 6. Convert Date
    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )


    # 7. Fill missing City
    df["City"] = df["City"].fillna(
        "Bengaluru"
    )


    # 8. Fill missing Transport Mode
    df["TransportMode"] = (
        df["TransportMode"]
        .replace("", pd.NA)
        .fillna("Unknown")
    )


    # 9. Fill missing Status
    df["Status"] = (
        df["Status"]
        .fillna("Unknown")
    )


    # ------------------------------------------------------
    # VALIDATE NUMERIC VALUES
    # ------------------------------------------------------

    # Distance cannot be negative
    df.loc[
        df["Distance_km"] < 0,
        "Distance_km"
    ] = pd.NA


    # Passenger count cannot be negative
    df.loc[
        df["PassengerCount"] < 0,
        "PassengerCount"
    ] = pd.NA


    # Trip duration cannot be negative
    df.loc[
        df["TripDuration_min"] < 0,
        "TripDuration_min"
    ] = pd.NA


    # Frequency cannot be negative
    df.loc[
        df["Frequency_per_day"] < 0,
        "Frequency_per_day"
    ] = pd.NA


    # Fare cannot be negative
    df.loc[
        df["Fare_INR"] < 0,
        "Fare_INR"
    ] = pd.NA


    # Occupancy should be between 0 and 100
    df.loc[
        ~df["OccupancyRate"].between(0, 100),
        "OccupancyRate"
    ] = pd.NA


    # Delay cannot be negative
    df.loc[
        df["Delay_min"] < 0,
        "Delay_min"
    ] = pd.NA


    # Latitude validation
    df.loc[
        ~df["Latitude"].between(-90, 90),
        "Latitude"
    ] = pd.NA


    # Longitude validation
    df.loc[
        ~df["Longitude"].between(-180, 180),
        "Longitude"
    ] = pd.NA


    # ------------------------------------------------------
    # REMOVE ROWS WITH CRITICAL INVALID DATA
    # ------------------------------------------------------

    df.dropna(
        subset=[
            "TransitID",
            "Date",
            "RouteID",
            "SourceStop",
            "DestinationStop",
            "Latitude",
            "Longitude"
        ],
        inplace=True
    )


    # ------------------------------------------------------
    # FILL REMAINING NUMERIC MISSING VALUES
    # ------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    for col in numeric_columns:

        df[col] = df[col].fillna(
            df[col].median()
        )


    # ------------------------------------------------------
    # SORT DATA
    # ------------------------------------------------------

    df.sort_values(
        by="Date",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )


    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    output_file = (
        "Clean_Data/"
        "Bengaluru_Transit_Clean.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )


    print("\nLOAD")
    print("-" * 40)
    print("Final Rows:", len(df))
    print("Clean file:", output_file)

    return df


# ==========================================================
# RUN BOTH ETL PROCESSES
# ==========================================================

print("\n")
print("#" * 60)
print("        BENGALURU DATA ETL PIPELINE")
print("#" * 60)


geospatial_df = clean_geospatial()

transit_df = clean_transit()


# ==========================================================
# FINAL SUMMARY
# ==========================================================

print("\n")
print("#" * 60)
print("              ETL COMPLETED")
print("#" * 60)

print(
    "\nGeospatial Clean Rows:",
    len(geospatial_df)
)

print(
    "Transit Clean Rows:",
    len(transit_df)
)

print("\nClean files created:")
print("1. Clean_Data/Bengaluru_Geospatial_Clean.csv")
print("2. Clean_Data/Bengaluru_Transit_Clean.csv")

print("\nETL process completed successfully!")