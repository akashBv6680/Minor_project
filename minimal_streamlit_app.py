# minimal_streamlit_app.py

import streamlit as st
import os
from dotenv import load_dotenv

st.title("Dotenv Test App")

try:
    load_dotenv()
    st.success("`python-dotenv` loaded successfully!")
    st.write(f"Example env var (if set): MY_TEST_VAR = {os.getenv('MY_TEST_VAR', 'Not Set')}")
    st.write("If you see this, `python-dotenv` is working.")
except Exception as e:
    st.error(f"Failed to load `python-dotenv`: {e}")
    st.write("This indicates `python-dotenv` is not installed or accessible.")

st.write("---")
st.write("This app tests if the `python-dotenv` library can be imported and used.")

