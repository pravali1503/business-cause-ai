
import pandas as pd

from backend.core.nlp_processor import (
    process_natural_language_query,
    validate_analysis_request
)


def create_sample_data():

    return pd.DataFrame({
        "Date": ["2025-01-01", "2025-02-01"],
        "Region": ["North", "South"],
        "Product": ["Laptop", "Mobile"],
        "Sales": [1000, 1500],
        "Profit": [200, 300]
    })


def test_contribution_question():

    df = create_sample_data()

    request = process_natural_language_query(
        "Which region contributed most to sales decrease?",
        df
    )

    assert request["success"] is True
    assert request["intent"] == "contribution"
    assert request["metric_column"] == "Sales"
    assert request["dimension_column"] == "Region"


def test_anomaly_question():

    df = create_sample_data()

    request = process_natural_language_query(
        "Show unusual sales values",
        df
    )

    assert request["success"] is True
    assert request["intent"] == "anomaly"
    assert request["metric_column"] == "Sales"


def test_trend_question():

    df = create_sample_data()

    request = process_natural_language_query(
        "Show sales trends over time",
        df
    )

    assert request["success"] is True
    assert request["intent"] == "trend"


def test_invalid_question():

    df = create_sample_data()

    request = process_natural_language_query(
        "Tell me something",
        df
    )

    assert request["success"] is False
    assert request["intent"] == "unknown"


def test_request_validation():

    df = create_sample_data()

    request = process_natural_language_query(
        "Which region contributed most to sales decrease?",
        df
    )

    valid, message = validate_analysis_request(
        request,
        df
    )

    assert valid is True
    assert message == "Analysis request validated successfully."
