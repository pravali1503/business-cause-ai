
import pandas as pd

from backend.core.contribution import analyze_contributions


def create_sample_data():
    data = {
        "Date": [
            "2025-01-01",
            "2025-01-01",
            "2025-02-01",
            "2025-02-01"
        ],
        "Region": [
            "North",
            "South",
            "North",
            "South"
        ],
        "Sales": [
            100,
            200,
            120,
            100
        ]
    }

    return pd.DataFrame(data)


def test_contribution_calculation():

    df = create_sample_data()

    result, overall_change = analyze_contributions(
        df,
        "Date",
        "Sales",
        "Region",
        "2025-01-01",
        "2025-01-01",
        "2025-02-01",
        "2025-02-01"
    )

    assert overall_change == -80

    north = result[result["Region"] == "North"].iloc[0]
    south = result[result["Region"] == "South"].iloc[0]

    assert north["Previous Value"] == 100
    assert north["Current Value"] == 120
    assert north["Change"] == 20

    assert south["Previous Value"] == 200
    assert south["Current Value"] == 100
    assert south["Change"] == -100

    assert round(north["Contribution (%)"], 2) == -25.00
    assert round(south["Contribution (%)"], 2) == 125.00


def test_zero_overall_change():

    df = pd.DataFrame({
        "Date": [
            "2025-01-01",
            "2025-01-01",
            "2025-02-01",
            "2025-02-01"
        ],
        "Region": [
            "North",
            "South",
            "North",
            "South"
        ],
        "Sales": [
            100,
            200,
            150,
            150
        ]
    })

    result, overall_change = analyze_contributions(
        df,
        "Date",
        "Sales",
        "Region",
        "2025-01-01",
        "2025-01-01",
        "2025-02-01",
        "2025-02-01"
    )

    assert overall_change == 0
    assert result["Contribution (%)"].isna().all()
