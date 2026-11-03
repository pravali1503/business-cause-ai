
import pandas as pd


MAX_FILE_SIZE = 20 * 1024 * 1024


def validate_upload(uploaded_file):

    if uploaded_file is None:
        return False, "Please upload a CSV file."

    if not uploaded_file.name.lower().endswith(".csv"):
        return False, "Only CSV files are allowed."

    if uploaded_file.size == 0:
        return False, "The uploaded file is empty."

    if uploaded_file.size > MAX_FILE_SIZE:
        return False, "File size must not exceed 20 MB."

    return True, "File validation successful."


def validate_dataframe(df):

    if df is None or df.empty:
        return False, "The dataset is empty."

    if len(df.columns) == 0:
        return False, "No columns found in the dataset."

    if df.columns.duplicated().any():
        return False, "Duplicate column names detected."

    if all(str(col).strip() == "" for col in df.columns):
        return False, "Column names are missing."

    if df.dropna(how="all").empty:
        return False, "The dataset contains only blank rows."

    return True, "Dataset validation successful."
