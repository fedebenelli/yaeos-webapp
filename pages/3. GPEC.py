import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from io import BytesIO
import yaeos


def get_fig(psats, critical_lines, x_col, y_col):

    fig = go.Figure()

    if x_col == "T":
        for i, psat in enumerate(psats):
            fig.add_scatter(
                x=psat["T"],
                y=psat[y_col],
                mode="lines",
                name=f"Pure saturation pressure {i+1}",
            )

    for critical_line in critical_lines:
        if critical_line:
            fig.add_scatter(
                x=critical_line[x_col],
                y=critical_line[y_col],
                mode="lines",
                name="Critical Line",
            )

    return fig


if "critical_constants" in st.session_state:
    if len(st.session_state.critical_constants) > 1:
        model_setter = st.session_state.model_setter
        model_params = st.session_state.critical_constants

        z0 = [1, 0]
        zi = [0, 1]

        model = st.session_state.model

        gpec = yaeos.GPEC(model)

        pure_psat_1, pure_psat_2 = gpec._pures
        critical_line_21 = gpec._cl21
        critical_line_12 = gpec._cl12
        critical_line_hpll = gpec._cl_ll

        print(gpec._cep12)
        print(gpec._cep21)
        print(gpec._cep_ll)

        c1, c2 = st.columns(2)

        with c1:
            fig = get_fig(
                [pure_psat_1, pure_psat_2],
                [critical_line_21, critical_line_12, critical_line_hpll],
                "T",
                "P",
            )
            st.plotly_chart(fig, use_container_width=False)
        with c2:
            fig = get_fig(
                [pure_psat_1, pure_psat_2],
                [critical_line_21, critical_line_12, critical_line_hpll],
                "a",
                "P",
            )
            st.plotly_chart(fig, use_container_width=False)

        df_1 = pd.DataFrame(pure_psat_1)
        df_2 = pd.DataFrame(pure_psat_2)
        df_cl21 = pd.DataFrame(critical_line_21)
        df_cl12 = pd.DataFrame(critical_line_12)
        df_clhpll = pd.DataFrame(critical_line_hpll)

        buffer = BytesIO()
        file_name = "gpec.xlsx"

        with pd.ExcelWriter(buffer) as writer:
            df_1.to_excel(writer, sheet_name="pure_psat_1")
            df_2.to_excel(writer, sheet_name="pure_psat_2")
            df_cl21.to_excel(writer, sheet_name="critical_line")
            df_clhpll.to_excel(writer, sheet_name="critical_line_hpll")

        st.download_button(
            label="Download as Excel File",
            data=buffer.getvalue(),
            file_name=file_name,
            mime="application/vnd.ms-excel",
        )

        c1, c2  = st.columns(2)
        with c1:
            st.subheader("Pxy Diagram")
            temperature = st.number_input(
                "Temperature [K]",
                min_value=0.0,
                value=300.0,
                step=1.0,
            )
            pxys = gpec.calc_pxy(temperature)

            fig = go.Figure()
            for pxy in pxys:
                if pxy:
                    z1 = pxy["a"]
                    w1 = pxy.reference_phase_compositions[:, 0]
                    p = pxy["P"]

                    fig.add_scatter(
                        x=z1,
                        y=p,
                        mode="lines",
                        name="Bubble Line",
                    )
                    fig.add_scatter(
                        x=w1,
                        y=p,
                        mode="lines",
                        name="Dew Line",
                    )
                    st.plotly_chart(fig, use_container_width=False)
    else:
        st.warning("Please select a model and its parameters first.")
else:
    st.warning("Please select a model and its parameters first.")
