
import pandas as pd
from statsmodels.tsa.seasonal import STL


def prepare_time_series(df, date_column, metric_column):

    data = df[[date_column, metric_column]].copy()

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

    if data.empty:
        raise ValueError(
            "No valid date and numeric metric observations were found."
        )

    data[date_column] = data[date_column].dt.normalize()

    daily_data = (
        data.groupby(date_column)[metric_column]
        .sum()
        .reset_index()
        .sort_values(date_column)
        .reset_index(drop=True)
    )

    if len(daily_data) < 3:
        raise ValueError(
            "At least 3 different dates are required for trend analysis."
        )

    daily_data["Rolling Average"] = (
        daily_data[metric_column]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    return daily_data


def perform_stl_decomposition(
    trend_df,
    date_column,
    metric_column,
    period=7
):

    if period < 2:
        raise ValueError(
            "The seasonality period must be at least 2."
        )

    if len(trend_df) < 2 * period:
        raise ValueError(
            f"At least {2 * period} observations are required "
            f"for a seasonality period of {period}. "
            f"The current dataset has {len(trend_df)} observations."
        )

    values = pd.to_numeric(
        trend_df[metric_column],
        errors="coerce"
    )

    if values.isna().any():
        raise ValueError(
            "The metric contains missing or invalid values."
        )

    if values.nunique() < 2:
        raise ValueError(
            "STL decomposition requires variation in the metric values."
        )

    model = STL(
        values.astype(float),
        period=period,
        robust=True
    )

    result = model.fit()

    return pd.DataFrame({
        date_column: trend_df[date_column].values,
        "Observed": values.values,
        "Trend": result.trend,
        "Seasonal": result.seasonal,
        "Residual": result.resid
    })
