
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(
    df,
    date_column,
    metric_column,
    contamination=0.1
):

    data = df.copy()

    # Convert date and metric columns

    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )

    data[metric_column] = pd.to_numeric(
        data[metric_column],
        errors="coerce"
    )

    # Remove invalid records

    data = data.dropna(
        subset=[date_column, metric_column]
    )

    # Group business values by date

    daily_data = (
        data.groupby(date_column)[metric_column]
        .sum()
        .reset_index()
    )

    daily_data = daily_data.sort_values(
        by=date_column
    ).reset_index(drop=True)

    # Validate dataset

    if len(daily_data) < 5:

        raise ValueError(
            "At least 5 different dates are required "
            "for anomaly detection."
        )

    if daily_data[metric_column].nunique() < 2:

        raise ValueError(
            "Anomaly detection requires variation "
            "in the metric values."
        )

    if not 0 < contamination <= 0.5:

        raise ValueError(
            "Contamination must be greater than 0 "
            "and at most 0.5."
        )

    # Create Isolation Forest model

    model = IsolationForest(
        contamination=contamination,
        random_state=42
    )

    # Train model and detect anomalies

    predictions = model.fit_predict(
        daily_data[[metric_column]]
    )

    scores = model.decision_function(
        daily_data[[metric_column]]
    )

    # Store results

    daily_data["Anomaly"] = [
        "Anomaly" if prediction == -1 else "Normal"
        for prediction in predictions
    ]

    daily_data["Anomaly Score"] = scores

    return daily_data
