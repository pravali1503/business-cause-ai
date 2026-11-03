
import streamlit as st
import pandas as pd

from components.auth_ui import require_login
from backend.services.llm_service import generate_business_insight

from backend.core.nlp_processor import (
    process_natural_language_query,
    validate_analysis_request
)


st.set_page_config(
    page_title="AI Assistant | RootCause AI",
    page_icon="🤖",
    layout="wide"
)

require_login()


# PAGE HEADER

st.title("🤖 RootCause AI Assistant")

st.write(
    "Ask questions about your business performance, "
    "segment contributions, anomalies, and trends."
)

st.divider()


# GET DATASET FROM SESSION

def get_uploaded_dataset():

    preferred_keys = [
        "cleaned_df",
        "uploaded_df",
        "df",
        "data"
    ]

    for key in preferred_keys:

        value = st.session_state.get(key)

        if isinstance(value, pd.DataFrame):
            return value

    for value in st.session_state.values():

        if isinstance(value, pd.DataFrame):
            return value

    return None


# GET INVESTIGATION RESULTS

def get_investigation_context():

    context = {}

    if "period_result" in st.session_state:

        result = st.session_state.period_result

        settings = st.session_state.get(
            "analysis_settings",
            {}
        )

        context["Period Analysis"] = {
            "Metric": settings.get(
                "metric_column",
                "Not available"
            ),
            "Previous Period": (
                f"{settings.get('previous_start')} to "
                f"{settings.get('previous_end')}"
            ),
            "Current Period": (
                f"{settings.get('current_start')} to "
                f"{settings.get('current_end')}"
            ),
            "Previous Value": result.get("previous_value"),
            "Current Value": result.get("current_value"),
            "Absolute Change": result.get("absolute_change"),
            "Percentage Change": result.get("percentage_change"),
            "Status": result.get("status"),
            "Previous Records": result.get("previous_rows"),
            "Current Records": result.get("current_rows")
        }

    if "contribution_result" in st.session_state:

        contribution_df = st.session_state.contribution_result

        dimension = st.session_state.get(
            "selected_contribution_dimension",
            "Dimension"
        )

        context["Segment Contribution"] = {
            "Dimension": dimension,
            "Overall Change": st.session_state.get(
                "contribution_overall_change"
            ),
            "Top Segments": contribution_df.head(10).to_dict(
                orient="records"
            )
        }

    if "anomaly_result" in st.session_state:

        anomaly_df = st.session_state.anomaly_result

        anomaly_count = int(
            (anomaly_df["Anomaly"] == "Anomaly").sum()
        )

        normal_count = int(
            (anomaly_df["Anomaly"] == "Normal").sum()
        )

        context["Anomaly Detection"] = {
            "Total Observations": len(anomaly_df),
            "Anomalies Detected": anomaly_count,
            "Normal Observations": normal_count,
            "Anomaly Details": anomaly_df[
                anomaly_df["Anomaly"] == "Anomaly"
            ].head(10).to_dict(orient="records")
        }

    if "trend_result" in st.session_state:

        trend_df = st.session_state.trend_result

        settings = st.session_state.get(
            "trend_settings",
            {}
        )

        metric = settings.get("metric_column")

        if metric and metric in trend_df.columns:

            context["Trend Analysis"] = {
                "First Observation": float(
                    trend_df[metric].iloc[0]
                ),
                "Latest Observation": float(
                    trend_df[metric].iloc[-1]
                ),
                "First-to-Last Change": float(
                    trend_df[metric].iloc[-1]
                    - trend_df[metric].iloc[0]
                ),
                "Number of Observations": len(trend_df)
            }

    return context


# INVESTIGATION CONTEXT

analysis_context = get_investigation_context()

if analysis_context:

    st.success(
        "Investigation results are available to the AI Assistant."
    )

else:

    st.warning(
        "No investigation results found. Upload a dataset and complete "
        "at least the Period Comparison Analysis on the dashboard first."
    )


# SUGGESTED QUESTIONS

st.subheader("Suggested Questions")

suggested_questions = [
    "Why did the business metric increase or decrease?",
    "Which segment contributed most to the overall change?",
    "Which segments performed poorly?",
    "What do the anomaly detection results indicate?",
    "Explain the business trend in simple English.",
    "What should the business investigate next?"
]

columns = st.columns(2)

for index, question in enumerate(suggested_questions):

    with columns[index % 2]:

        if st.button(
            question,
            key=f"suggestion_{index}",
            use_container_width=True
        ):

            st.session_state.pending_question = question


st.divider()


# CHAT HISTORY

if "ai_chat_history" not in st.session_state:

    st.session_state.ai_chat_history = []


# CLEAR CHAT

if st.button("Clear Conversation"):

    st.session_state.ai_chat_history = []

    st.session_state.pop(
        "pending_question",
        None
    )

    st.rerun()


# DISPLAY PREVIOUS MESSAGES

for message in st.session_state.ai_chat_history:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# CHAT INPUT

user_question = st.chat_input(
    "Ask a question about your business data..."
)

if "pending_question" in st.session_state:

    user_question = st.session_state.pop(
        "pending_question"
    )


# PROCESS USER QUESTION

if user_question:

    if not analysis_context:

        st.warning(
            "Please complete a business investigation before asking "
            "questions about its results."
        )

    else:

        previous_history = (
            st.session_state.ai_chat_history.copy()
        )

        with st.chat_message("user"):

            st.markdown(user_question)

        # NLP PREPROCESSING

        dataset = get_uploaded_dataset()

        nlp_context = {}

        if dataset is not None:

            try:

                nlp_request = process_natural_language_query(
                    user_question,
                    dataset
                )

                if nlp_request["success"]:

                    valid, validation_message = (
                        validate_analysis_request(
                            nlp_request,
                            dataset
                        )
                    )

                    if valid:

                        nlp_context = {
                            "Detected Intent": nlp_request["intent"],
                            "Detected Metric": nlp_request[
                                "metric_column"
                            ],
                            "Detected Dimension": nlp_request[
                                "dimension_column"
                            ],
                            "Validation": validation_message
                        }

                        with st.expander(
                            "View NLP Processing Result"
                        ):

                            st.success(
                                "Business question processed successfully."
                            )

                            st.write(
                                "**Intent:**",
                                nlp_request["intent"]
                            )

                            st.write(
                                "**Metric:**",
                                nlp_request["metric_column"]
                            )

                            st.write(
                                "**Dimension:**",
                                nlp_request["dimension_column"]
                            )

                    else:

                        with st.expander(
                            "View NLP Processing Result"
                        ):

                            st.warning(validation_message)

                else:

                    with st.expander(
                        "View NLP Processing Result"
                    ):

                        st.info(nlp_request["message"])

            except Exception as error:

                st.warning(
                    f"NLP preprocessing could not be completed: {error}"
                )

        else:

            st.info(
                "Dataset columns are not available in session state. "
                "The assistant will use the completed investigation results."
            )

        # ADD NLP DETAILS TO INVESTIGATION CONTEXT

        final_context = analysis_context.copy()

        if nlp_context:

            final_context["NLP Processing"] = nlp_context

        # GENERATE GROQ AI RESPONSE

        with st.chat_message("assistant"):

            with st.spinner(
                "Understanding your question and analyzing business results..."
            ):

                try:

                    answer = generate_business_insight(
                        question=user_question,
                        analysis_context=final_context,
                        chat_history=previous_history
                    )

                    st.markdown(answer)

                    st.session_state.ai_chat_history.append({
                        "role": "user",
                        "content": user_question
                    })

                    st.session_state.ai_chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                except Exception as error:

                    st.error(
                        f"Unable to generate AI response: {error}"
                    )
