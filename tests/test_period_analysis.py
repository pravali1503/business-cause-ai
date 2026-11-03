
import pandas as pd

from backend.core.period_analysis import analyze_periods


def create_sample_data():

    data = {
        "Date": [
            "2025-01-01",
            "2025-01-02",
            "2025-02-01",
            "2025-02-02"
        ],
        "Sales": [
            100,
            200,
            150,
            250
        ]
    }

    return pd.DataFrame(data)


def test_period_comparison():

    df = create_sample_data()

    result = analyze_periods(
        df,
        "Date",
        "Sales",
        "2025-01-01",
        "2025-01-02",
        "2025-02-01",
        "2025-02-02"
    )

    assert result["previous_value"] == 300
    assert result["current_value"] == 400
    assert result["absolute_change"] == 100
    assert result["percentage_change"] == 33.33333333333333
    assert result["status"] == "Increased"
    assert result["previous_rows"] == 2
    assert result["current_rows"] == 2


def test_zero_previous_period_value():

    df = pd.DataFrame({
        "Date": [
            "2025-01-01",
            "2025-02-01"
        ],
        "Sales": [
            0,
            100
        ]
    })

    result = analyze_periods(
        df,
        "Date",
        "Sales",
        "2025-01-01",
        "2025-01-01",
        "2025-02-01",
        "2025-02-01"
    )

    assert result["previous_value"] == 0
    assert result["current_value"] == 100
    assert result["absolute_change"] == 100
    assert result["percentage_change"] is None
    assert result["status"] == "Increased"


def test_decreased_performance():

    df = pd.DataFrame({
        "Date": [
            "2025-01-01",
            "2025-02-01"
        ],
        "Sales": [
            500,
            300
        ]
    })

    result = analyze_periods(
        df,
        "Date",
        "Sales",
        "2025-01-01",
        "2025-01-01",
        "2025-02-01",
        "2025-02-01"
    )

    assert result["absolute_change"] == -200
    assert result["percentage_change"] == -40
    assert result["status"] == "Decreased"
