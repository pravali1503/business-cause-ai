
import streamlit as st
import pandas as pd

from components.metrics_cards import (
    display_dataset_metrics,
    display_quality_metrics,
    display_investigation_status
)

from components.auth_ui import require_login

from backend.core.data_processor import get_data_quality

from backend.services.database_service import get_user_investigations


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Dashboard | RootCause AI",
    page_icon="📊",
    layout="wide"
)


# AUTHENTICATION

require_login()

user = st.session_state.user


# DASHBOARD HEADER

st.title("📊 Dashboard")

st.write(
    f"Welcome back, {user['name']}! "
    "Here is your business investigation overview."
)

st.divider()


# DATASET OVERVIEW

st.subheader("Dataset Overview")

if "business_data" in st.session_state:

    df = st.session_state.business_data

    quality = get_data_quality(df)

    # DISPLAY DATASET METRICS

    display_dataset_metrics(quality)

    st.success(
        f"Current dataset: "
        f"{st.session_state.get('dataset_name', 'Unnamed Dataset')}"
    )

    # DATASET PREVIEW

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )

    # DATA QUALITY

    st.subheader("Data Quality")

    display_quality_metrics(quality)

    if quality["missing_values"] > 0:

        st.warning(
            "Your dataset contains missing values."
        )

    if quality["duplicate_rows"] > 0:

        st.warning(
            "Your dataset contains duplicate records."
        )

    if (
        quality["missing_values"] == 0
        and quality["duplicate_rows"] == 0
    ):

        st.success(
            "Your dataset has no missing values or duplicate rows."
        )

else:

    st.info(
        "No dataset has been uploaded yet. "
        "Go to the Investigation page to upload your business CSV file."
    )


st.divider()


# INVESTIGATION STATUS

st.subheader("Investigation Status")

display_investigation_status()


# TREND ANALYSIS STATUS

if "trend_result" in st.session_state:

    st.success(
        "Trend and seasonality analysis has been performed."
    )

else:

    st.info(
        "Trend and seasonality analysis has not been performed yet."
    )


st.divider()


# RECENT INVESTIGATIONS

st.subheader("Recent Investigations")

try:

    investigations = get_user_investigations(
        user["id"]
    )

    if investigations:

        recent_investigations = investigations[:5]

        history_data = []

        for investigation in recent_investigations:

            history_data.append({

                "Dataset": investigation["dataset_name"],

                "Metric": investigation["metric"],

                "Previous Period": investigation["previous_period"],

                "Current Period": investigation["current_period"],

                "Created At": investigation["created_at"]

            })

        history_df = pd.DataFrame(history_data)

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "Showing your five most recent saved investigations."
        )

    else:

        st.info(
            "You have not saved any investigations yet. "
            "Complete an investigation and save it to see it here."
        )

except Exception as error:

    st.error(
        f"Unable to load recent investigations: {error}"
    )


st.divider()


# QUICK NAVIGATION

st.subheader("Quick Navigation")

st.write(
    "Use the sidebar to access the following sections:"
)

col1, col2 = st.columns(2)

with col1:

    st.page_link(
        "pages/2_Investigation.py",
        label="Start New Investigation",
        icon=":material/analytics:"
    )

    st.page_link(
        "pages/3_AI_Assistant.py",
        label="Open AI Assistant",
        icon=":material/smart_toy:"
    )

with col2:

    st.page_link(
        "pages/4_History.py",
        label="View Investigation History",
        icon=":material/history:"
    )

    st.page_link(
        "pages/5_Profile.py",
        label="View My Profile",
        icon=":material/account_circle:"
    )


st.divider()

st.caption(
    "RootCause AI | Business Root-Cause and Contribution Investigator"
)
