import pandas as pd

import streamlit as st

from constants import AR_MODELS


class ModelSettings:
    def __init__(self):
        ...

    def select_model(self):
        st.subheader("⚙️ Selección de modelo")
        st.write(
            "Selecciona el modelo que deseas utilizar para la predicción."
        )

        selected_model = st.selectbox(
            "Modelo de Ar",
            options=AR_MODELS,
            index=0,
            format_func=lambda x: x.replace("_", " "),
        )

        st.session_state.selected_model = selected_model
        st.session_state.model_setter = AR_MODELS[selected_model]["setter"]

    def edit_critical_constants(self):

        if "critical_constants" not in st.session_state:
            st.session_state.critical_constants = pd.DataFrame(
                columns=["Tc", "Pc", "w"]
            )

        editor = st.data_editor(
            st.session_state.critical_constants, num_rows="dynamic", hide_index=True
        )

        if st.button("Save data"):
            st.session_state.critical_constants = editor

    def show_critical_constants(self):
        st.subheader("Critical Constants")
        try:
            st.dataframe(st.session_state.critical_constants, use_container_width=True)
        except:
            st.write("No critical constants available.")


orchestra = ModelSettings()