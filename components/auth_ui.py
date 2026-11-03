
import streamlit as st


def initialize_session():

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None


def require_login():

    initialize_session()

    if not st.session_state.authenticated:

        st.warning("Please log in to access this page.")

        st.stop()

    return True


def logout():

    st.session_state.authenticated = False

    st.session_state.user = None

    st.rerun()
