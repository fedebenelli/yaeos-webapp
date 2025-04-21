import numpy as np

import pandas as pd

import streamlit as st

from constants import AR_MODELS, AR_MIXING_RULES, GE_MODELS, setup_nrtl


class ModelSettings:
    def __init__(self):
        ...

    def select_model(self):
        st.subheader("Model Selection")
        st.write(
            "Select the thermodynamic model to be used in the calculations."
        )

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Model")
            st.write(
                "The model is used to calculate the fugacity coefficients of the components in the mixture."
            )
            selected_model = st.selectbox(
                "Model to use:",
                options=AR_MODELS,
                index=0,
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
                index=0,
                format_func=lambda x: x.replace("_", " "),
            )

        st.session_state.selected_model = selected_model
        st.session_state.model_setter = AR_MODELS[selected_model]["setter"]
        st.session_state.mixing_rule = mixing_rule
        st.session_state.mixing_rule_setter = AR_MIXING_RULES[mixing_rule]["setter"]

    def edit_critical_constants(self):

        st.subheader("Critical Constants")
        st.write(
            "The critical constants are used to calculate the model parameters."
        )

        if "critical_constants" not in st.session_state:
            st.session_state.critical_constants = pd.DataFrame(
                columns=["Tc [K]", "Pc [bar]", "w"],
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

    def setup_model(self):
        self.edit_critical_constants()

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
                delta_1 = st.data_editor(delta_1, num_rows=nc, hide_index=True, key="delta_1")
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

            st.text("Define the $G^E$ model parameters")
            if ge_model_name == "NRTL":
                st.subheader("NRTL Parameters")
                ge_model = ge_model_setter(nc)
            if mixing_rule_name == "MHV1":
                st.subheader("Mixing Rule Parameters")
                q = st.number_input(label="q", value=-0.5, step=0.01)
                mixing_rule = mixing_rule_setter(q=q, ge=ge_model)

            # elif ge_model_name == "HV":
            #     mixing_rule = setup_hv(nc, ge_model_setter)



        if model_name in (
            "SoaveRedlichKong", "PengRobinson76", "PengRobinson78"
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
                critical_z=zc
            )

        st.session_state.nc = nc
        st.session_state.model = model


def setup_qmr(nc, setter):
    kij = np.zeros((nc, nc))
    lij = np.zeros((nc, nc))
    
    kij = pd.DataFrame(kij)
    lij = pd.DataFrame(lij)

    st.subheader("Interaction Parameters")                
    st.subheader("$k_{ij}$ matrix")
    kij = st.data_editor(kij, num_rows=nc, hide_index=True, key="kij")
    st.subheader("$l_{ij}$ matrix")
    lij = st.data_editor(lij, num_rows=nc, hide_index=True, key="lij")

    kij = np.array(kij.values, order="F", dtype=np.float64)
    lij = np.array(lij.values, order="F", dtype=np.float64)

    return setter(kij=kij, lij=lij)


def setup_qmrtd(nc, setter):
    kij_0 = np.zeros((nc, nc))
    kij_inf = np.zeros((nc, nc))
    lij = np.zeros((nc, nc))
    tref = np.zeros((nc, nc))

    kij_0 = pd.DataFrame(kij_0)
    kij_inf = pd.DataFrame(kij_inf)
    lij = pd.DataFrame(lij)
    tref = pd.DataFrame(tref)

    st.subheader("Interaction Parameters")                

    st.subheader("$k_{ij}^0$ matrix")
    kij_0 = st.data_editor(kij_0, num_rows=nc, hide_index=True, key="kij_0")
    st.subheader("$k_{ij}^\infty$ matrix")
    kij_inf = st.data_editor(kij_inf, num_rows=nc, hide_index=True, key="kij_inf")
    st.subheader("$l_{ij}$ matrix")
    lij = st.data_editor(lij, num_rows=nc, hide_index=True, key="lij")
    kij_0 = np.array(kij_0.values, order="F", dtype=np.float64)
    kij_inf = np.array(kij_inf.values, order="F", dtype=np.float64)
    lij = np.array(lij.values, order="F", dtype=np.float64)

    st.subheader("$T_{ref}$ matrix")
    tref = st.data_editor(tref, num_rows=nc, hide_index=True, key="tref")

    return setter(kij_0=kij_0, kij_inf=kij_inf, lij=lij, t_ref=tref)


orchestra = ModelSettings()