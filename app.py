import pandas as pd

import streamlit as st

from settings import orchestra

st.set_page_config(page_title="Aplicación de Ejemplos", layout="wide")
st.sidebar.title("Yaeos WebApp")

st.title("Yaeos WebApp")
st.markdown(
    """
Welcome to the yaeos WebApp!

This is a simple web application that allows you to do Equations of State (EOS)
calculations using the `yaeos` library.

You can use the sidebar to select the kind of calculation you want to run.

It is important to first visit the "Load Parameters" page to load the
fundamental parameters of the system you want to study.
"""
)
