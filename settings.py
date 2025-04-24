import numpy as np

import pandas as pd

import streamlit as st

from constants import AR_MODELS, AR_MIXING_RULES, GE_MODELS, setup_nrtl

from setters import (
    setup_qmr,
    setup_qmrtd,
    setup_nrtl,
)


class ModelSettings:
    def __init__(self): ...

    def select_model(self):
        st.subheader("Model Selection")
        st.write(
            "Select the thermodynamic model to be used in the calculations."
        )

        if "model_ar_index" not in st.session_state:
            st.session_state.model_ar_index = 0
        if "mixing_rule_index" not in st.session_state:
            st.session_state.mixing_rule_index = 0
        if "model_ge_index" not in st.session_state:
            st.session_state.model_ge_index = 0

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Model")
            st.write(
                "The model is used to calculate the fugacity coefficients of the components in the mixture."
            )
            selected_model = st.selectbox(
                "Model to use:",
                options=AR_MODELS,
                index=st.session_state.model_ar_index,
                format_func=lambda x: x.replace("_", " "),
            )
        with c2:
            st.subheader("Mixing Rule")
            st.write(
                "The mixing rule is used to calculate the interaction parameters between the components in the mixture."
            )
            mixing_rule = st.selectbox(
                "Mixing Rule",
                options=AR_MIXING_RULES,
                index=st.session_state.mixing_rule_index,
                format_func=lambda x: x.replace("_", " "),
            )

        st.session_state.model_ar_index = list(AR_MODELS.keys()).index(
            selected_model
        )
        st.session_state.mixing_rule_index = list(
            AR_MIXING_RULES.keys()
        ).index(mixing_rule)

        st.session_state.selected_model = selected_model
        st.session_state.model_setter = AR_MODELS[selected_model]["setter"]
        st.session_state.mixing_rule = mixing_rule
        st.session_state.mixing_rule_setter = AR_MIXING_RULES[mixing_rule][
            "setter"
        ]

    def edit_critical_constants(self):

        st.subheader("Critical Constants")
        st.write(
            "The critical constants are used to calculate the model parameters."
        )

        if "critical_constants" not in st.session_state:
            st.session_state.critical_constants = pd.DataFrame(
                columns=["name", "Tc [K]", "Pc [bar]", "w"],
            )
            st.session_state.critical_constants = st.session_state.critical_constants.set_index("name")

        editor = st.data_editor(
            st.session_state.critical_constants,
            num_rows="dynamic",
            hide_index=False,
        )

        print(editor)

        if st.button("Save critical constants"):
            st.session_state.critical_constants = editor

    def show_critical_constants(self):
        st.subheader("Critical Constants")
        try:
            st.dataframe(
                st.session_state.critical_constants, use_container_width=True
            )
        except:
            st.write("No critical constants available.")

    def setup_model(self):

        c1, c2 = st.columns(2)

        with c1:
            self.edit_critical_constants()
        with c2:
            self.select_model()

        Tc = st.session_state.critical_constants["Tc [K]"].values
        Pc = st.session_state.critical_constants["Pc [bar]"].values
        w = st.session_state.critical_constants["w"].values

        model_name = st.session_state.selected_model
        model_setter = st.session_state.model_setter
        mixing_rule_name = st.session_state.mixing_rule
        mixing_rule_setter = st.session_state.mixing_rule_setter

        nc = len(Tc)

        if model_name == "RKPR":
            delta_1 = np.zeros(nc)
            k = np.zeros(nc)
            zc = np.zeros(nc)

            delta_1 = pd.DataFrame(delta_1)
            k = pd.DataFrame(k)
            zc = pd.DataFrame(zc)

            st.subheader("RKPR Parameters")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.subheader("$k$ matrix")
                k = st.data_editor(k, num_rows=nc, hide_index=True, key="k")
            with c2:
                st.subheader("$\delta_1$")
                delta_1 = st.data_editor(
                    delta_1, num_rows=nc, hide_index=True, key="delta_1"
                )
            with c3:
                st.subheader("$z_c$")
                zc = st.data_editor(zc, num_rows=nc, hide_index=True, key="zc")

            delta_1 = np.array(delta_1.values, order="F", dtype=np.float64)
            k = np.array(k.values, order="F", dtype=np.float64)

            if all(delta_1 == 0):
                delta_1 = None
            if all(k == 0):
                k = None

        if mixing_rule_name == "QMR":
            mixing_rule = setup_qmr(nc, mixing_rule_setter)
        elif mixing_rule_name == "QMRTD":
            mixing_rule = setup_qmrtd(nc, mixing_rule_setter)
        elif mixing_rule_name in ("MHV1", "HV"):
            ge_model_name = st.selectbox(r"$G^E$ Model", GE_MODELS, index=0)
            ge_model_setter = GE_MODELS[ge_model_name]["setter"]

            if ge_model_name == "NRTL":
                ge_model = ge_model_setter(nc)

            if mixing_rule_name == "MHV1":
                st.subheader("Mixing Rule Parameters")
                q = st.number_input(label="q", value=-0.5, step=0.01)
                mixing_rule = mixing_rule_setter(q=q, ge=ge_model)
            elif mixing_rule_name == "HV":
                mixing_rule = mixing_rule_setter(ge_model)

        if model_name in (
            "SoaveRedlichKwong",
            "PengRobinson76",
            "PengRobinson78",
        ):
            model = model_setter(
                critical_temperatures=Tc,
                critical_pressures=Pc,
                acentric_factors=w,
                mixrule=mixing_rule,
            )
        elif model_name == "RKPR":
            model = model_setter(
                critical_temperatures=Tc,
                critical_pressures=Pc,
                acentric_factors=w,
                k=k,
                delta_1=delta_1,
                mixrule=mixing_rule,
                critical_z=zc,
            )

        st.session_state.nc = nc
        st.session_state.model = model


orchestra = ModelSettings()
