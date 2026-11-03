
import streamlit as st

from backend.services.database_service import initialize_database
from backend.services.auth_service import register_user, login_user
from components.auth_ui import initialize_session


st.set_page_config(
    page_title="RootCause AI",
    page_icon="📊",
    layout="wide"
)

initialize_database()
initialize_session()


def authentication_page():

    st.title("📊 RootCause AI")

    st.subheader(
        "Business Root-Cause and Contribution Investigator"
    )

    st.write(
        "Investigate business performance, identify contributing "
        "segments and generate AI-powered insights."
    )

    st.divider()

    login_tab, register_tab = st.tabs(
        ["Login", "Create Account"]
    )

    with login_tab:

        st.subheader("Welcome Back")

        with st.form("login_form"):

            email = st.text_input("Email Address")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login_button:

                if not email.strip() or not password:

                    st.warning(
                        "Please enter your email and password."
                    )

                else:

                    success, user, message = login_user(
                        email,
                        password
                    )

                    if success:

                        st.session_state.authenticated = True
                        st.session_state.user = user

                        st.rerun()

                    else:

                        st.error(message)

    with register_tab:

        st.subheader("Create Your Account")

        with st.form("register_form"):

            name = st.text_input("Full Name")
            email = st.text_input("Email Address")

            password = st.text_input(
                "Create Password",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm Password",
                type="password"
            )

            register_button = st.form_submit_button(
                "Register",
                use_container_width=True
            )

            if register_button:

                if not name.strip() or not email.strip():

                    st.warning(
                        "Please complete all required fields."
                    )

                elif password != confirm_password:

                    st.error("Passwords do not match.")

                else:

                    success, message = register_user(
                        name,
                        email,
                        password
                    )

                    if success:
                        st.success(message)

                    else:
                        st.error(message)


def main():

    if not st.session_state.authenticated:

        login_page = st.Page(
            authentication_page,
            title="Login",
            icon=":material/login:",
            default=True
        )

        navigation = st.navigation(
            [login_page],
            position="sidebar"
        )

    else:

        dashboard_page = st.Page(
            "pages/1_Dashboard.py",
            title="Dashboard",
            icon=":material/dashboard:",
            default=True
        )

        investigation_page = st.Page(
            "pages/2_Investigation.py",
            title="Investigation",
            icon=":material/analytics:"
        )

        ai_page = st.Page(
            "pages/3_AI_Assistant.py",
            title="AI Assistant",
            icon=":material/smart_toy:"
        )

        history_page = st.Page(
            "pages/4_History.py",
            title="History",
            icon=":material/history:"
        )

        profile_page = st.Page(
            "pages/5_Profile.py",
            title="Profile",
            icon=":material/account_circle:"
        )

        navigation = st.navigation(
            {
                "Workspace": [
                    dashboard_page,
                    investigation_page,
                    ai_page,
                    history_page
                ],
                "Account": [
                    profile_page
                ]
            },
            position="sidebar"
        )

    navigation.run()


if __name__ == "__main__":
    main()
