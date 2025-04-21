import yaeos

import numpy as np

import pandas as pd

import streamlit as st


def setup_nrtl(nc):

    a, b, c = np.zeros((nc, nc)), np.zeros((nc, nc)), np.zeros((nc, nc))

    a = pd.DataFrame(a)
    b = pd.DataFrame(b)
    c = pd.DataFrame(c)

    c1, c2, c3 = st.columns(3)

    with c1:
        a = st.data_editor(a, key="a", num_rows=nc, use_container_width=True)
    with c2:
        b = st.data_editor(b, key="b", num_rows=nc, use_container_width=True)
    with c3:
        c = st.data_editor(c, key="c", num_rows=nc, use_container_width=True)

    a = np.array(a.to_numpy(), order="F")
    b = np.array(b.to_numpy(), order="F")
    c = np.array(c.to_numpy(), order="F")

    return yaeos.NRTL(a, b, c)


AR_MODELS = {
    "PengRobinson76": {"setter": yaeos.PengRobinson76},
    "PengRobinson78": {"setter": yaeos.PengRobinson78},
    "SoaveRedlichKwong": {"setter": yaeos.SoaveRedlichKwong},
    "RKPR": {"setter": yaeos.RKPR},
    # "PSRK": {"setter": yaeos.PSRK},
}

AR_MIXING_RULES = {
    "QMR": {"setter": yaeos.QMR},
    "QMRTD": {"setter": yaeos.QMRTD},
    "MHV1": {"setter": yaeos.MHV},
    "HV": {"setter": yaeos.HV},
}

GE_MODELS = {
    "UNIFAC_VLE": {"setter": yaeos.UNIFACVLE},
    "NRTL": {"setter": setup_nrtl},
}
