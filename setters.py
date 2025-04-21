import streamlit as st
import numpy as np
import pandas as pd
import yaeos


def setup_qmr(nc, setter):
    t1, t2 = st.tabs(["kij", "lij"])

    st.subheader("Interaction Parameters")
    with t1:
        kij = binary_parameter(nc, r"$k_{ij}$")

    with t2:
        lij = binary_parameter(nc, r"$l_{ij}$")
    return setter(kij=kij, lij=lij)


def setup_qmrtd(nc, setter):
    c1, c2, c3, c4 = st.tabs(
        ["$k_{ij}^0$", "$k_{ij}^\infty$", "$l_{ij}$", "$T^{*}$"]
    )

    with c1:
        kij_0 = binary_parameter(nc, r"$k_{ij}^0$")
    with c2:
        kij_inf = binary_parameter(nc, r"$k_{ij}^\infty$")
    with c3:
        lij = binary_parameter(nc, r"$l_{ij}$")
    with c4:
        tref = binary_parameter(nc, r"$T^{*}$")
    return setter(kij_0=kij_0, kij_inf=kij_inf, lij=lij, t_ref=tref)


def setup_nrtl(nc):
    st.subheader("NRTL Parameters")
    st.write(
        r"""
    $G^E = nRT \cdot \sum_i x_i \frac{\sum_j x_j \tau_{ji} G_{ji}}{\sum_j x_j G_{ji}}$

    with:
    - $\tau_{ij} = A_{ij} + \frac{B_{ij}}{T}$
    - $G_{ij} = exp(-C\tau_{ij})$
    """
    )
    a, b, c = np.zeros((nc, nc)), np.zeros((nc, nc)), np.zeros((nc, nc))

    t1, t2, t3 = st.tabs(["$A_{ij}$", "$B_{ij}$", "$C_{ij}$"])

    with t1:
        a = binary_parameter(nc, r"$A_{ij}$")
    with t2:
        b = binary_parameter(nc, r"$B_{ij}$")
    with t3:
        c = binary_parameter(nc, r"$C_{ij}$")

    return yaeos.NRTL(a, b, c)


def binary_parameter(nc, name):

    bip = np.zeros((nc, nc), order="F")
    bip = pd.DataFrame(bip)

    if name not in st.session_state:
        st.session_state[name] = bip
    elif nc != len(st.session_state[name]):
        st.session_state[name] = bip

    st.subheader(f"{name} matrix")
    editor = st.data_editor(
        st.session_state[name],
        num_rows=nc,
        hide_index=True,
        key="editor_" + name,
    )
    bip = np.array(editor.values, order="F", dtype=np.float64)

    if st.button(f"Save ${name}$ matrix", key="save_" + name):
        st.session_state[name] = editor

    return bip
