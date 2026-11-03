import pandas as pd
import io

from backend.utils.validators import validate_dataframe


def load_csv(file_data):
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
    last_error = None

    for encoding in encodings:
        try:
            df = pd.read_csv(io.BytesIO(file_data), encoding=encoding)
            valid, message = validate_dataframe(df)

            if not valid:
                raise ValueError(message)

            return df

        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(f"Unable to read CSV encoding: {last_error}")


def get_data_preview(df):
    return df.head(10)


def get_column_information(df):
    information = []

    for column in df.columns:
        information.append({
            "Column": column,
            "Data Type": str(df[column].dtype),
            "Non-Null Values": int(df[column].count()),
            "Missing Values": int(df[column].isna().sum()),
            "Unique Values": int(df[column].nunique())
        })

    return pd.DataFrame(information)


def get_data_quality(df):
    total_rows = len(df)
    total_columns = len(df.columns)
    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    blank_rows = int(df.isna().all(axis=1).sum())

    missing_percentage = (
        (missing_values / (total_rows * total_columns)) * 100
        if total_rows > 0 and total_columns > 0
        else 0
    )

    return {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "missing_values": missing_values,
        "missing_percentage": round(missing_percentage, 2),
        "duplicate_rows": duplicate_rows,
        "blank_rows": blank_rows
    }


def clean_data(df, missing_strategy, duplicate_strategy):
    cleaned_df = df.copy()

    # Convert empty and whitespace-only cells into missing values
    cleaned_df = cleaned_df.replace(r"^\s*$", pd.NA, regex=True)

    original_rows = len(cleaned_df)
    original_missing = int(cleaned_df.isna().sum().sum())
    original_duplicates = int(cleaned_df.duplicated().sum())

    # Handle duplicate records
    if duplicate_strategy == "Remove duplicate rows":
        cleaned_df = cleaned_df.drop_duplicates()

    # Handle missing values
    if missing_strategy == "Remove rows with missing values":
        cleaned_df = cleaned_df.dropna()

    elif missing_strategy == "Fill numeric with median and text with mode":
        for column in cleaned_df.columns:

            if cleaned_df[column].isna().any():

                if pd.api.types.is_numeric_dtype(cleaned_df[column]):
                    median_value = cleaned_df[column].median()

                    if pd.notna(median_value):
                        cleaned_df[column] = cleaned_df[column].fillna(median_value)

                else:
                    mode_values = cleaned_df[column].mode(dropna=True)

                    if not mode_values.empty:
                        cleaned_df[column] = cleaned_df[column].fillna(
                            mode_values.iloc[0]
                        )

    final_missing = int(cleaned_df.isna().sum().sum())
    final_duplicates = int(cleaned_df.duplicated().sum())

    summary = {
        "original_rows": original_rows,
        "cleaned_rows": len(cleaned_df),
        "removed_rows": original_rows - len(cleaned_df),
        "original_missing": original_missing,
        "remaining_missing": final_missing,
        "original_duplicates": original_duplicates,
        "remaining_duplicates": final_duplicates
    }

    return cleaned_df, summary