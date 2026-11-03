
import pandas as pd


def analyze_contributions(
    df,
    date_column,
    metric_column,
    dimension_column,
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

    data = data.dropna(
        subset=[date_column, metric_column]
    )

    data[dimension_column] = (
        data[dimension_column]
        .fillna("Missing")
        .astype(str)
        .str.strip()
        .replace("", "Missing")
    )

    previous_data = data[
        (data[date_column] >= pd.Timestamp(previous_start)) &
        (data[date_column] <= pd.Timestamp(previous_end))
    ]

    current_data = data[
        (data[date_column] >= pd.Timestamp(current_start)) &
        (data[date_column] <= pd.Timestamp(current_end))
    ]

    previous_totals = previous_data.groupby(
        dimension_column
    )[metric_column].sum()

    current_totals = current_data.groupby(
        dimension_column
    )[metric_column].sum()

    result = pd.concat(
        [previous_totals, current_totals],
        axis=1,
        keys=["Previous Value", "Current Value"]
    ).fillna(0)

    result["Change"] = (
        result["Current Value"] - result["Previous Value"]
    )

    overall_change = result["Change"].sum()

    if overall_change != 0:

        result["Contribution (%)"] = (
            result["Change"] / overall_change
        ) * 100

    else:

        result["Contribution (%)"] = None

    result = result.reset_index()

    result = result.sort_values(
        by="Change",
        key=lambda values: values.abs(),
        ascending=False
    )

    result = result.reset_index(drop=True)

    return result, overall_change
