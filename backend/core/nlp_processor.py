
import re
import pandas as pd


def normalize_question(question):

    if not question or not question.strip():
        raise ValueError("Please enter a business question.")

    question = question.lower().strip()

    question = re.sub(r"\s+", " ", question)

    return question


def identify_metric(question, df):

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    question_words = re.findall(
        r"[a-zA-Z0-9_]+",
        question
    )

    for column in numeric_columns:

        column_name = str(column).lower()

        if column_name in question:
            return column

        column_words = column_name.replace("_", " ").split()

        if column_words and all(
            word in question_words for word in column_words
        ):
            return column

    aliases = {
        "sales": ["sale", "sales"],
        "revenue": ["revenue", "income"],
        "profit": ["profit", "earnings"],
        "quantity": ["quantity", "units", "items sold"],
        "orders": ["orders", "order count"],
        "customers": ["customers", "customer count"]
    }

    for column in numeric_columns:

        column_name = str(column).lower()

        for key, words in aliases.items():

            if key in column_name:

                if any(word in question for word in words):
                    return column

    if len(numeric_columns) == 1:
        return numeric_columns[0]

    return None


def identify_dimension(question, df):

    date_columns = [
        column
        for column in df.columns
        if "date" in str(column).lower()
    ]

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    dimension_columns = [
        column
        for column in df.columns
        if column not in date_columns
        and column not in numeric_columns
    ]

    for column in dimension_columns:

        column_name = str(column).lower()

        if column_name in question:
            return column

        column_words = column_name.replace("_", " ").split()

        if column_words and all(
            word in question.split() for word in column_words
        ):
            return column

    aliases = {
        "region": ["region", "area", "location", "city"],
        "product": ["product", "item", "category"],
        "customer": ["customer", "client", "customer segment"],
        "segment": ["segment", "customer group"]
    }

    for column in dimension_columns:

        column_name = str(column).lower()

        for key, words in aliases.items():

            if key in column_name:

                if any(word in question for word in words):
                    return column

    if len(dimension_columns) == 1:
        return dimension_columns[0]

    return None


def identify_intent(question):

    contribution_words = [
        "contribution",
        "contribute",
        "contributed",
        "impact",
        "segment",
        "reason for change",
        "which region",
        "which product"
    ]

    anomaly_words = [
        "anomaly",
        "anomalies",
        "unusual",
        "abnormal",
        "outlier",
        "unexpected"
    ]

    trend_words = [
        "trend",
        "trends",
        "over time",
        "seasonality",
        "seasonal",
        "pattern"
    ]

    comparison_words = [
        "compare",
        "comparison",
        "difference",
        "increased",
        "decreased",
        "change between",
        "period"
    ]

    summary_words = [
        "summary",
        "summarize",
        "overview",
        "overall performance"
    ]

    if any(word in question for word in contribution_words):
        return "contribution"

    if any(word in question for word in anomaly_words):
        return "anomaly"

    if any(word in question for word in trend_words):
        return "trend"

    if any(word in question for word in comparison_words):
        return "comparison"

    if any(word in question for word in summary_words):
        return "summary"

    return "unknown"


def process_natural_language_query(question, df):

    question = normalize_question(question)

    if df is None or df.empty:
        raise ValueError(
            "Please upload a valid business dataset first."
        )

    metric_column = identify_metric(
        question,
        df
    )

    dimension_column = identify_dimension(
        question,
        df
    )

    intent = identify_intent(question)

    if intent == "unknown":

        return {
            "success": False,
            "intent": "unknown",
            "metric_column": metric_column,
            "dimension_column": dimension_column,
            "message": (
                "I could not identify the requested analysis. "
                "Try asking about contribution, comparison, "
                "anomalies, trends or business summary."
            )
        }

    if intent != "summary" and metric_column is None:

        return {
            "success": False,
            "intent": intent,
            "metric_column": None,
            "dimension_column": dimension_column,
            "message": (
                "I could not identify the numeric business metric. "
                "Please mention a metric such as Sales, Revenue or Profit."
            )
        }

    if intent == "contribution" and dimension_column is None:

        return {
            "success": False,
            "intent": intent,
            "metric_column": metric_column,
            "dimension_column": None,
            "message": (
                "Please specify a business dimension such as "
                "Region, Product or Customer Segment."
            )
        }

    return {
        "success": True,
        "intent": intent,
        "metric_column": metric_column,
        "dimension_column": dimension_column,
        "message": "Your business question was processed successfully."
    }


def validate_analysis_request(request, df):

    if not isinstance(request, dict):
        return False, "Invalid analysis request."

    if not request.get("success"):
        return False, request.get(
            "message",
            "Unable to process the question."
        )

    intent = request.get("intent")

    allowed_intents = [
        "contribution",
        "anomaly",
        "trend",
        "comparison",
        "summary"
    ]

    if intent not in allowed_intents:
        return False, "Unsupported analysis type."

    metric_column = request.get("metric_column")

    if metric_column is not None:

        if metric_column not in df.columns:
            return False, "Invalid business metric."

        if not pd.api.types.is_numeric_dtype(
            df[metric_column]
        ):
            return False, "The selected metric must be numeric."

    dimension_column = request.get("dimension_column")

    if dimension_column is not None:

        if dimension_column not in df.columns:
            return False, "Invalid business dimension."

    if intent == "contribution":

        if dimension_column is None:
            return False, "A business dimension is required."

        if dimension_column == metric_column:
            return False, "Metric and dimension cannot be the same column."

    return True, "Analysis request validated successfully."
