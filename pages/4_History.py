
import json
import streamlit as st

from components.auth_ui import require_login

from backend.services.database_service import (
    get_user_investigations,
    get_investigation_by_id,
    delete_investigation
)


st.set_page_config(
    page_title="Investigation History | RootCause AI",
    page_icon="📚",
    layout="wide"
)

require_login()


st.title("📚 Investigation History")

st.write(
    "View and manage your previously saved business investigations."
)

st.divider()


user = st.session_state.user

investigations = get_user_investigations(user["id"])


if not investigations:

    st.info(
        "You have not saved any investigations yet. "
        "Complete a business analysis and save it to see it here."
    )

else:

    st.subheader("Your Saved Investigations")

    st.metric(
        "Total Investigations",
        len(investigations)
    )

    for investigation in investigations:

        with st.expander(
            f"Investigation #{investigation['id']} — "
            f"{investigation['dataset_name'] or 'Unnamed Dataset'}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Metric:**",
                    investigation["metric"] or "Not available"
                )

                st.write(
                    "**Previous Period:**",
                    investigation["previous_period"] or "Not available"
                )

            with col2:

                st.write(
                    "**Current Period:**",
                    investigation["current_period"] or "Not available"
                )

                st.write(
                    "**Saved At:**",
                    investigation["created_at"]
                )

            st.divider()

            try:

                summary = json.loads(
                    investigation["result_summary"]
                )

                st.subheader("Investigation Results")

                if isinstance(summary, dict):

                    st.json(summary)

                else:

                    st.write(summary)

            except (json.JSONDecodeError, TypeError):

                st.write(
                    investigation["result_summary"]
                )

            st.divider()

            if st.button(
                "Delete Investigation",
                key=f"delete_{investigation['id']}"
            ):

                deleted = delete_investigation(
                    investigation["id"],
                    user["id"]
                )

                if deleted:

                    st.success("Investigation deleted successfully.")

                    st.rerun()

                else:

                    st.error("Unable to delete this investigation.")
