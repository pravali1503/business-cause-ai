
import streamlit as st

from components.auth_ui import require_login, logout
from backend.services.database_service import get_user_by_email


require_login()

user = st.session_state.user


# PAGE TITLE

st.title("👤 My Profile")

st.write(
    "View your account information and manage your RootCause AI account."
)

st.divider()


# PROFILE INFORMATION

st.subheader("Personal Information")

col1, col2 = st.columns([1, 2])

with col1:

    st.markdown(
        """
        <div style="
            width:120px;
            height:120px;
            border-radius:50%;
            background:linear-gradient(135deg,#4776E6,#8E54E9);
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:48px;
            color:white;
            font-weight:bold;
            margin:auto;
        ">
        👤
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    st.subheader(user["name"])

    st.caption("RootCause AI User")

    st.write(f"**Email:** {user['email']}")

    st.write(f"**User ID:** {user['id']}")


st.divider()


# ACCOUNT DETAILS

st.subheader("Account Details")

try:

    account = get_user_by_email(user["email"])

    if account is not None:

        st.write(
            f"**Account Created:** {account['created_at']}"
        )

except Exception as error:

    st.warning(
        f"Unable to load account creation details: {error}"
    )


st.divider()


# ACCOUNT SUMMARY

st.subheader("Account Summary")

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Account Status",
        "Active"
    )

with col2:

    st.metric(
        "Saved Investigations",
        "View History"
    )

    st.page_link(
        "pages/4_History.py",
        label="Open Investigation History",
        icon=":material/history:"
    )


st.divider()


# LOGOUT

st.subheader("Account Actions")

st.write(
    "Log out of your RootCause AI account when you finish your work."
)

if st.button(
    "Logout",
    type="primary",
    use_container_width=True
):

    logout()
