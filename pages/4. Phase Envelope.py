import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from io import BytesIO


def p_wilson(z, T, Tc, Pc, w):
    print(z)
    print(Pc)
    P = 1.0/np.sum(z * Pc * np.exp(5.373 * (1 + w)*(1 - Tc/T)))
    return P

if "critical_constants" in st.session_state:
    if len(st.session_state.critical_constants) > 1:
        dew, bub = None, None
        model_setter = st.session_state.model_setter
        model_params = st.session_state.critical_constants

        model = st.session_state.model

        nc = len(model_params["Tc [K]"])
        Tc, Pc, w = (
            model_params["Tc [K]"].values,
            model_params["Pc [bar]"].values,
            model_params["w"].values,
        )
        t0 = pd.to_numeric(model_params["Tc [K]"]).mean()
        p0 = pd.to_numeric(model_params["Pc [bar]"]).mean()
        z = np.ones(nc)
        z = z/sum(z)

        c1, c2 = st.columns(2)
        with c1:

            c11, c12 = st.columns(2)
            with c11:
                st.subheader("Fluid composition (moles)")
                editor = st.data_editor(z, use_container_width=False)

                z = np.array(editor/sum(editor))
            with c12:
                st.subheader("Mole Fractions")
                st.dataframe(
                    pd.DataFrame(
                        {
                            "Component": model_params.index,
                            "Mole Fraction": z,
                        }
                    ),
                    use_container_width=False,
                )

            if st.button("Calculate Phase Envelope"):
                dew = model.phase_envelope_pt(z, kind="dew", t0=t0, p0=1)

                t0 = 500
                while p0 > 1:
                    p0 = p_wilson(z, t0, Tc, Pc, w)
                    t0 -= 10
                print(t0, p0)
                sat = model.saturation_pressure(z, temperature=t0, p0=p0)
                print(sat)

                bub = model.phase_envelope_pt(
                    z, kind="bubble", t0=t0, p0=p0
                )

                dew = model.phase_envelope_pt(
                    z, kind="dew", t0=400, p0=1
                )

                p0 = max([max(bub["P"]), max(dew["P"])]) * 10

                t0 = max([max(bub["T"]), max(dew["T"])]) + 100

                liq = model.phase_envelope_pt(z, kind="liquid-liquid", t0=t0, p0=p0)

        with c2:
            fig = go.Figure()
            for env in [dew, bub, liq]:
                if env:
                    fig.add_trace(
                        go.Scatter(
                            x=env["T"],
                            y=env["P"],
                            mode="lines",
                            name="Phase Envelope",
                        )
                    )
                    fig.add_scatter(
                        x=env["Tc"],
                        y=env["Pc"],
                        mode="markers",
                        name="CP",
                    )

            fig.update_xaxes(title_text="Temperature [K]",)
            fig.update_yaxes(title_text="Pressure [bar]",)
            st.plotly_chart(fig, use_container_width=True, points=1000)

    else:
        st.warning("Please select a model and its parameters first.")
else:
    st.warning("Please select a model and its parameters first.")