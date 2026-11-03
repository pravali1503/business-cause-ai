
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from components.auth_ui import require_login

from backend.core.data_processor import (
    load_csv,
    get_data_preview,
    get_column_information,
    get_data_quality,
    clean_data
)

from backend.core.period_analysis import (
    analyze_periods,
    get_numeric_columns
)

from backend.core.contribution import analyze_contributions

from backend.core.anomaly_detection import detect_anomalies

from backend.core.trend_analysis import (
    prepare_time_series,
    perform_stl_decomposition
)

from backend.core.report_generator import generate_investigation_pdf

from backend.utils.validators import validate_upload

from backend.services.database_service import save_investigation

from components.charts import (
    create_period_comparison_chart,
    create_contribution_chart
)


# AUTHENTICATION

require_login()

user = st.session_state.user


# PAGE TITLE

st.title("🔍 Business Investigation")

st.write(
    "Upload your business dataset, analyze performance changes, "
    "identify contributing segments and generate investigation reports."
)

st.divider()


# CSV DATASET UPLOAD

st.header("1. Upload Business Dataset")

uploaded_file = st.file_uploader(
    "Choose your CSV file",
    type=["csv"],
    key="investigation_csv_upload"
)

if uploaded_file is not None:

    st.write("Selected file:", uploaded_file.name)

    if st.button(
        "Process Dataset",
        use_container_width=True
    ):

        valid, message = validate_upload(uploaded_file)

        if not valid:

            st.error(message)

        else:

            try:

                with st.spinner("Processing dataset..."):

                    df = load_csv(uploaded_file.getvalue())

                    st.session_state.business_data = df
                    st.session_state.dataset_name = uploaded_file.name

                    keys_to_clear = [
                        "cleaned_data",
                        "cleaning_summary",
                        "period_result",
                        "selected_metric",
                        "analysis_settings",
                        "contribution_result",
                        "selected_contribution_dimension",
                        "contribution_overall_change",
                        "anomaly_result",
                        "anomaly_settings",
                        "trend_result",
                        "trend_settings"
                    ]

                    for key in keys_to_clear:
                        st.session_state.pop(key, None)

                st.success(
                    "Dataset uploaded and processed successfully!"
                )

            except Exception as error:

                st.error(
                    f"Unable to process CSV: {error}"
                )


# CHECK DATASET

if "business_data" not in st.session_state:

    st.info(
        "Please upload a CSV dataset to begin your investigation."
    )

    st.stop()


df = st.session_state.business_data


# DATASET OVERVIEW

st.divider()

st.header("2. Dataset Overview")

quality = get_data_quality(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Rows",
    quality["total_rows"]
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


st.subheader("Dataset Preview")

st.dataframe(
    get_data_preview(df),
    use_container_width=True
)


st.subheader("Column Information")

st.dataframe(
    get_column_information(df),
    use_container_width=True
)


# DATA QUALITY REPORT

st.subheader("Data Quality Report")

q1, q2, q3 = st.columns(3)

q1.metric(
    "Missing Percentage",
    f"{quality['missing_percentage']}%"
)

q2.metric(
    "Blank Rows",
    quality["blank_rows"]
)

q3.metric(
    "Duplicate Rows",
    quality["duplicate_rows"]
)


if quality["missing_values"] > 0:

    st.warning("Missing values detected.")


if quality["duplicate_rows"] > 0:

    st.warning("Duplicate records detected.")


if (
    quality["missing_values"] == 0
    and quality["duplicate_rows"] == 0
):

    st.success(
        "No missing values or duplicate rows detected."
    )


# DATA CLEANING

st.divider()

st.header("3. Data Cleaning")

st.write(
    "Choose how to handle missing values and duplicate records."
)


missing_strategy = st.selectbox(
    "How should missing values be handled?",
    [
        "Keep missing values",
        "Remove rows with missing values",
        "Fill numeric with median and text with mode"
    ]
)


duplicate_strategy = st.selectbox(
    "How should duplicate records be handled?",
    [
        "Keep duplicate rows",
        "Remove duplicate rows"
    ]
)


if st.button(
    "Clean Dataset",
    use_container_width=True
):

    cleaned_df, summary = clean_data(
        df,
        missing_strategy,
        duplicate_strategy
    )

    st.session_state.cleaned_data = cleaned_df
    st.session_state.cleaning_summary = summary

    keys_to_clear = [
        "period_result",
        "analysis_settings",
        "contribution_result",
        "selected_contribution_dimension",
        "contribution_overall_change",
        "anomaly_result",
        "anomaly_settings",
        "trend_result",
        "trend_settings"
    ]

    for key in keys_to_clear:
        st.session_state.pop(key, None)

    st.success(
        "Data cleaning completed successfully!"
    )


# CLEANING RESULTS

if "cleaned_data" in st.session_state:

    cleaned_df = st.session_state.cleaned_data
    summary = st.session_state.cleaning_summary

    st.subheader("Cleaning Summary")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Original Rows",
        summary["original_rows"]
    )

    c2.metric(
        "Cleaned Rows",
        summary["cleaned_rows"]
    )

    c3.metric(
        "Removed Rows",
        summary["removed_rows"]
    )

    c4, c5, c6 = st.columns(3)

    c4.metric(
        "Original Missing Values",
        summary["original_missing"]
    )

    c5.metric(
        "Remaining Missing Values",
        summary["remaining_missing"]
    )

    c6.metric(
        "Remaining Duplicates",
        summary["remaining_duplicates"]
    )

    st.subheader("Cleaned Dataset")

    st.dataframe(
        cleaned_df,
        use_container_width=True
    )

    if cleaned_df.empty:

        st.warning(
            "The cleaned dataset is empty. Change the cleaning options."
        )


# SELECT DATA FOR ANALYSIS

analysis_df = (
    st.session_state.cleaned_data
    if "cleaned_data" in st.session_state
    else df
)


if analysis_df.empty:

    st.warning(
        "No records are available for analysis."
    )

    st.stop()


st.divider()

st.header("4. Business Analysis")


# DATE AND METRIC SELECTION

date_columns = [
    column
    for column in analysis_df.columns
    if "date" in column.lower()
]

numeric_columns = get_numeric_columns(analysis_df)


if not date_columns:

    st.warning(
        "No date column was detected. Use a column whose name "
        "contains the word 'date'."
    )

    st.stop()


if not numeric_columns:

    st.warning(
        "No numeric metric columns were found."
    )

    st.stop()


col1, col2 = st.columns(2)


with col1:

    date_column = st.selectbox(
        "Select Date Column",
        date_columns
    )


with col2:

    metric_column = st.selectbox(
        "Select Business Metric",
        numeric_columns
    )


# ANOMALY DETECTION

st.divider()

st.header("5. Anomaly Detection")

st.write(
    "Identify unusual changes in the business metric over time "
    "using the Isolation Forest algorithm."
)


contamination = st.slider(
    "Expected proportion of unusual observations",
    min_value=0.01,
    max_value=0.30,
    value=0.10,
    step=0.01
)


if st.button(
    "Detect Anomalies",
    use_container_width=True
):

    try:

        anomaly_df = detect_anomalies(
            analysis_df,
            date_column,
            metric_column,
            contamination
        )

        st.session_state.anomaly_result = anomaly_df

        st.session_state.anomaly_settings = {
            "date_column": date_column,
            "metric_column": metric_column,
            "contamination": contamination
        }

        st.success(
            "Anomaly detection completed!"
        )

    except ValueError as error:

        st.error(str(error))

    except Exception as error:

        st.error(
            f"Unable to perform anomaly detection: {error}"
        )


# ANOMALY RESULTS

if "anomaly_result" in st.session_state:

    current_settings = {
        "date_column": date_column,
        "metric_column": metric_column,
        "contamination": contamination
    }

    if st.session_state.anomaly_settings == current_settings:

        anomaly_df = st.session_state.anomaly_result

        anomaly_count = int(
            (anomaly_df["Anomaly"] == "Anomaly").sum()
        )

        normal_count = int(
            (anomaly_df["Anomaly"] == "Normal").sum()
        )

        a1, a2 = st.columns(2)

        a1.metric(
            "Anomalies Detected",
            anomaly_count
        )

        a2.metric(
            "Normal Observations",
            normal_count
        )

        anomaly_chart = go.Figure()

        normal_data = anomaly_df[
            anomaly_df["Anomaly"] == "Normal"
        ]

        unusual_data = anomaly_df[
            anomaly_df["Anomaly"] == "Anomaly"
        ]

        anomaly_chart.add_trace(
            go.Scatter(
                x=anomaly_df[date_column],
                y=anomaly_df[metric_column],
                mode="lines",
                name="Business Metric",
                line=dict(width=2, color="#3498DB")
            )
        )

        anomaly_chart.add_trace(
            go.Scatter(
                x=normal_data[date_column],
                y=normal_data[metric_column],
                mode="markers",
                name="Normal",
                marker=dict(color="green", size=8)
            )
        )

        anomaly_chart.add_trace(
            go.Scatter(
                x=unusual_data[date_column],
                y=unusual_data[metric_column],
                mode="markers",
                name="Anomaly",
                marker=dict(
                    color="red",
                    size=12,
                    symbol="x"
                ),
                text=unusual_data["Anomaly Score"],
                hovertemplate=(
                    "Date: %{x}<br>"
                    "Metric: %{y}<br>"
                    "Anomaly Score: %{text}<extra></extra>"
                )
            )
        )

        anomaly_chart.update_layout(
            template="plotly_dark",
            title="Business Metric Anomaly Detection",
            xaxis_title="Date",
            yaxis_title=metric_column,
            hovermode="x unified"
        )

        st.plotly_chart(
            anomaly_chart,
            use_container_width=True
        )

        st.subheader("Anomaly Details")

        st.dataframe(
            anomaly_df,
            use_container_width=True
        )

        st.download_button(
            "Download Anomaly Report",
            data=anomaly_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="anomaly_report.csv",
            mime="text/csv"
        )

        st.caption(
            "An anomaly is an unusual observation, not automatic "
            "proof of a business problem."
        )


# TREND AND SEASONALITY ANALYSIS

st.divider()

st.header("6. Trend and Seasonality Analysis")

st.write(
    "Study how the selected business metric changes over time "
    "and identify possible repeating patterns."
)


seasonality_period = st.selectbox(
    "Select seasonality period",
    options=[7, 12, 30],
    format_func=lambda value: f"{value} observations"
)


if st.button(
    "Analyze Trend and Seasonality",
    use_container_width=True
):

    try:

        trend_df = prepare_time_series(
            analysis_df,
            date_column,
            metric_column
        )

        st.session_state.trend_result = trend_df

        st.session_state.trend_settings = {
            "date_column": date_column,
            "metric_column": metric_column,
            "period": seasonality_period
        }

        st.success(
            "Trend analysis completed!"
        )

    except ValueError as error:

        st.error(str(error))

    except Exception as error:

        st.error(
            f"Unable to perform trend analysis: {error}"
        )


# TREND RESULTS

if "trend_result" in st.session_state:

    current_settings = {
        "date_column": date_column,
        "metric_column": metric_column,
        "period": seasonality_period
    }

    if st.session_state.trend_settings == current_settings:

        trend_df = st.session_state.trend_result

        st.subheader("Business Performance Trend")

        trend_chart = go.Figure()

        trend_chart.add_trace(
            go.Scatter(
                x=trend_df[date_column],
                y=trend_df[metric_column],
                mode="lines+markers",
                name="Business Metric"
            )
        )

        trend_chart.add_trace(
            go.Scatter(
                x=trend_df[date_column],
                y=trend_df["Rolling Average"],
                mode="lines",
                name="Rolling Average",
                line=dict(width=3, dash="dash")
            )
        )

        trend_chart.update_layout(
            template="plotly_dark",
            title="Business Performance Over Time",
            xaxis_title="Date",
            yaxis_title=metric_column,
            hovermode="x unified"
        )

        st.plotly_chart(
            trend_chart,
            use_container_width=True
        )

        first_value = float(
            trend_df[metric_column].iloc[0]
        )

        last_value = float(
            trend_df[metric_column].iloc[-1]
        )

        total_change = last_value - first_value

        st.subheader("Trend Summary")

        t1, t2, t3 = st.columns(3)

        t1.metric(
            "First Observation",
            f"{first_value:,.2f}"
        )

        t2.metric(
            "Latest Observation",
            f"{last_value:,.2f}"
        )

        t3.metric(
            "First-to-Last Change",
            f"{total_change:,.2f}"
        )

        st.subheader(
            "STL Trend and Seasonality Decomposition"
        )

        try:

            decomposition_df = perform_stl_decomposition(
                trend_df,
                date_column,
                metric_column,
                seasonality_period
            )

            component_chart = go.Figure()

            for component in [
                "Observed",
                "Trend",
                "Seasonal",
                "Residual"
            ]:

                component_chart.add_trace(
                    go.Scatter(
                        x=decomposition_df[date_column],
                        y=decomposition_df[component],
                        mode="lines",
                        name=component
                    )
                )

            component_chart.update_layout(
                template="plotly_dark",
                title="STL Decomposition Components",
                xaxis_title="Date",
                yaxis_title="Component Value",
                hovermode="x unified"
            )

            st.plotly_chart(
                component_chart,
                use_container_width=True
            )

            st.dataframe(
                decomposition_df,
                use_container_width=True
            )

            st.download_button(
                "Download Trend and Seasonality Report",
                data=decomposition_df.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="trend_seasonality_report.csv",
                mime="text/csv"
            )

        except ValueError as error:

            st.info(
                f"STL decomposition is unavailable: {error} "
                "The trend chart is still available."
            )


# PERIOD COMPARISON ANALYSIS

st.divider()

st.header("7. Period Comparison Analysis")

st.write(
    "Compare the business metric between two selected date periods."
)


date_values = pd.to_datetime(
    analysis_df[date_column],
    errors="coerce"
).dropna()


if date_values.empty:

    st.warning(
        "The selected date column has no valid dates."
    )

    st.stop()


min_date = date_values.min()
max_date = date_values.max()


col1, col2 = st.columns(2)


with col1:

    st.subheader("Previous Period")

    previous_start = st.date_input(
        "Previous Period Start",
        value=min_date.date(),
        key="previous_start_date"
    )

    previous_end = st.date_input(
        "Previous Period End",
        value=min_date.date(),
        key="previous_end_date"
    )


with col2:

    st.subheader("Current Period")

    current_start = st.date_input(
        "Current Period Start",
        value=max_date.date(),
        key="current_start_date"
    )

    current_end = st.date_input(
        "Current Period End",
        value=max_date.date(),
        key="current_end_date"
    )


if st.button(
    "Analyze Business Performance",
    use_container_width=True
):

    if previous_start > previous_end:

        st.error(
            "Previous period start must be before its end."
        )

    elif current_start > current_end:

        st.error(
            "Current period start must be before its end."
        )

    elif not (
        previous_end < current_start
        or current_end < previous_start
    ):

        st.error(
            "The two comparison periods must not overlap."
        )

    else:

        try:

            result = analyze_periods(
                analysis_df,
                date_column,
                metric_column,
                previous_start,
                previous_end,
                current_start,
                current_end
            )

            st.session_state.period_result = result
            st.session_state.selected_metric = metric_column

            st.session_state.analysis_settings = {
                "date_column": date_column,
                "metric_column": metric_column,
                "previous_start": previous_start,
                "previous_end": previous_end,
                "current_start": current_start,
                "current_end": current_end
            }

            st.session_state.pop(
                "contribution_result",
                None
            )

            st.session_state.pop(
                "selected_contribution_dimension",
                None
            )

            st.session_state.pop(
                "contribution_overall_change",
                None
            )

            st.success(
                "Period comparison completed!"
            )

        except Exception as error:

            st.error(
                f"Period analysis failed: {error}"
            )


# DISPLAY PERIOD RESULTS

if "period_result" not in st.session_state:

    st.info(
        "Select your comparison periods and click Analyze Business Performance."
    )

    st.stop()


result = st.session_state.period_result

selected_metric = st.session_state.selected_metric


st.subheader("Business Performance Results")


if (
    result["previous_rows"] == 0
    or result["current_rows"] == 0
):

    st.warning(
        "One of the selected periods has no valid records. "
        "Choose date ranges that contain data."
    )

    st.stop()


r1, r2, r3 = st.columns(3)

r1.metric(
    "Previous Period",
    f"{result['previous_value']:,.2f}"
)

r2.metric(
    "Current Period",
    f"{result['current_value']:,.2f}"
)

r3.metric(
    "Absolute Change",
    f"{result['absolute_change']:,.2f}"
)


if result["percentage_change"] is not None:

    st.metric(
        "Percentage Change",
        f"{result['percentage_change']:.2f}%"
    )

else:

    st.warning(
        "Percentage change cannot be calculated because "
        "the previous period value is zero."
    )


if result["status"] == "Increased":

    st.success(
        f"{selected_metric} increased during the current period."
    )

elif result["status"] == "Decreased":

    st.error(
        f"{selected_metric} decreased during the current period."
    )

else:

    st.info(
        f"No change in {selected_metric} between the two periods."
    )


st.write(
    f"Previous period records: {result['previous_rows']}"
)

st.write(
    f"Current period records: {result['current_rows']}"
)


# SEGMENT CONTRIBUTION ANALYSIS

st.divider()

st.header("8. Segment Contribution Analysis")

st.write(
    "Identify which business segments contributed "
    "to the overall performance change."
)


dimension_columns = [
    column
    for column in analysis_df.columns
    if column != date_column and column != metric_column
]


if not dimension_columns:

    st.warning(
        "No additional dimensions available for contribution analysis."
    )

    st.stop()


dimension_column = st.selectbox(
    "Select Business Dimension",
    dimension_columns,
    key="contribution_dimension_widget"
)


if st.button(
    "Analyze Segment Contribution",
    use_container_width=True
):

    try:

        contribution_df, overall_change = analyze_contributions(
            analysis_df,
            date_column,
            metric_column,
            dimension_column,
            previous_start,
            previous_end,
            current_start,
            current_end
        )

        st.session_state.contribution_result = contribution_df

        st.session_state.selected_contribution_dimension = dimension_column

        st.session_state.contribution_overall_change = overall_change

    except Exception as error:

        st.error(
            f"Contribution analysis failed: {error}"
        )


# DISPLAY CONTRIBUTION RESULTS

if "contribution_result" in st.session_state:

    if (
        st.session_state.selected_contribution_dimension
        == dimension_column
    ):

        contribution_df = st.session_state.contribution_result

        overall_change = st.session_state.contribution_overall_change

        st.subheader("Contribution Results")

        st.metric(
            "Overall Change",
            f"{overall_change:,.2f}"
        )

        st.dataframe(
            contribution_df,
            use_container_width=True
        )

        st.subheader("Previous vs Current Period")

        comparison_chart = create_period_comparison_chart(
            contribution_df,
            dimension_column
        )

        st.plotly_chart(
            comparison_chart,
            use_container_width=True
        )

        st.subheader("Segment Contribution Chart")

        contribution_chart = create_contribution_chart(
            contribution_df,
            dimension_column
        )

        st.plotly_chart(
            contribution_chart,
            use_container_width=True
        )


        # CONTRIBUTION INTERPRETATION

        st.subheader("Contribution Interpretation")

        if overall_change == 0:

            st.info(
                "There is no overall change between the selected periods. "
                "Therefore, contribution percentages cannot be calculated."
            )

        else:

            positive = contribution_df[
                contribution_df["Change"] > 0
            ]

            negative = contribution_df[
                contribution_df["Change"] < 0
            ]

            if not positive.empty:

                largest_positive = positive.loc[
                    positive["Change"].idxmax()
                ]

                st.write(
                    f"**Largest positive contributor:** "
                    f"{largest_positive[dimension_column]} "
                    f"with a change of "
                    f"{largest_positive['Change']:,.2f}."
                )

            if not negative.empty:

                largest_negative = negative.loc[
                    negative["Change"].idxmin()
                ]

                st.write(
                    f"**Largest negative contributor:** "
                    f"{largest_negative[dimension_column]} "
                    f"with a change of "
                    f"{largest_negative['Change']:,.2f}."
                )

        st.caption(
            "Contribution describes each segment's mathematical "
            "share of the total change. It does not prove causation."
        )


        # DOWNLOAD CONTRIBUTION CSV

        contribution_csv = contribution_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download Contribution Report",
            data=contribution_csv,
            file_name="contribution_report.csv",
            mime="text/csv"
        )


        # SAVE INVESTIGATION

        st.divider()

        st.subheader("9. Save Investigation")

        st.write(
            "Save these results to your personal investigation history."
        )


        if st.button(
            "Save Investigation",
            use_container_width=True,
            key="save_current_investigation"
        ):

            try:

                period_summary = {
                    "previous_value": result["previous_value"],
                    "current_value": result["current_value"],
                    "absolute_change": result["absolute_change"],
                    "percentage_change": result["percentage_change"],
                    "status": result["status"],
                    "previous_rows": result["previous_rows"],
                    "current_rows": result["current_rows"]
                }

                summary_to_save = {
                    "period_analysis": period_summary,
                    "contribution_dimension": dimension_column,
                    "overall_contribution_change": overall_change,
                    "segment_contributions": contribution_df.to_dict(
                        orient="records"
                    )
                }

                saved_id = save_investigation(
                    user_id=user["id"],
                    dataset_name=st.session_state.get(
                        "dataset_name",
                        "Unnamed Dataset"
                    ),
                    metric=metric_column,
                    previous_period=(
                        f"{previous_start} to {previous_end}"
                    ),
                    current_period=(
                        f"{current_start} to {current_end}"
                    ),
                    result_summary=summary_to_save
                )

                st.success(
                    f"Investigation saved successfully! "
                    f"Investigation ID: {saved_id}"
                )

            except Exception as error:

                st.error(
                    f"Unable to save investigation: {error}"
                )


        # PDF INVESTIGATION REPORT

        st.divider()

        st.subheader("10. Download PDF Investigation Report")

        st.write(
            "Generate a report containing the period comparison, "
            "segment contribution results and key findings."
        )


        try:

            pdf_report = generate_investigation_pdf(
                dataset_name=st.session_state.get(
                    "dataset_name",
                    "Unnamed Dataset"
                ),
                metric=metric_column,
                previous_period=(
                    f"{previous_start} to {previous_end}"
                ),
                current_period=(
                    f"{current_start} to {current_end}"
                ),
                period_result=result,
                contribution_df=contribution_df,
                dimension_column=dimension_column
            )

            st.download_button(
                label="Download PDF Report",
                data=pdf_report,
                file_name="rootcause_investigation_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"Unable to generate PDF report: {error}"
            )
