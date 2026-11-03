import pandas as pd


def get_date_column(df):
    date_columns = []

    for column in df.columns:
        if "date" in column.lower():
            date_columns.append(column)

    return date_columns


def get_numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


def analyze_periods(
    df,
    date_column,
    metric_column,
    previous_start,
    previous_end,
    current_start,
    current_end
):

    data = df.copy()

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data[metric_column] = pd.to_numeric(
        data[metric_column],
        errors="coerce"
    )

    data = data.dropna(subset=[date_column, metric_column])

    previous_data = data[
        (data[date_column] >= pd.Timestamp(previous_start)) &
        (data[date_column] <= pd.Timestamp(previous_end))
    ]

    current_data = data[
        (data[date_column] >= pd.Timestamp(current_start)) &
        (data[date_column] <= pd.Timestamp(current_end))
    ]

    previous_value = previous_data[metric_column].sum()
    current_value = current_data[metric_column].sum()

    absolute_change = current_value - previous_value

    if previous_value != 0:
        percentage_change = (
            absolute_change / abs(previous_value)
        ) * 100
    else:
        percentage_change = None

    if absolute_change > 0:
        status = "Increased"
    elif absolute_change < 0:
        status = "Decreased"
    else:
        status = "No Change"

    return {
        "previous_value": previous_value,
        "current_value": current_value,
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "status": status,
        "previous_rows": len(previous_data),
        "current_rows": len(current_data)
    }