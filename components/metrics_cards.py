
import streamlit as st


def display_dataset_metrics(quality):

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Records",
        f"{quality['total_rows']:,}"
    )

    col2.metric(
        "Total Columns",
        quality["total_columns"]
    )

    col3.metric(
        "Missing Values",
        quality["missing_values"]
    )

    col4.metric(
        "Duplicate Rows",
        quality["duplicate_rows"]
    )


def display_quality_metrics(quality):

    col1, col2 = st.columns(2)

    col1.metric(
        "Missing Value Percentage",
        f"{quality['missing_percentage']}%"
    )

    col2.metric(
        "Blank Rows",
        quality["blank_rows"]
    )


def display_investigation_status():

    col1, col2, col3 = st.columns(3)

    with col1:

        if "period_result" in st.session_state:
            st.metric("Period Analysis", "Completed")
        else:
            st.metric("Period Analysis", "Not Started")

    with col2:

        if "contribution_result" in st.session_state:
            st.metric("Contribution Analysis", "Completed")
        else:
            st.metric("Contribution Analysis", "Not Started")

    with col3:

        if "anomaly_result" in st.session_state:
            st.metric("Anomaly Detection", "Completed")
        else:
            st.metric("Anomaly Detection", "Not Started")
