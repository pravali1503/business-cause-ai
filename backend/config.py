
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_setting(name, default=None):

    try:
        return st.secrets[name]

    except Exception:
        return os.getenv(name, default)


def get_groq_api_key():

    api_key = get_setting("GROQ_API_KEY")

    if not api_key:
        return None

    return api_key
