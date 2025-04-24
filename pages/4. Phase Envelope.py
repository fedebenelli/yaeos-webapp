import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from io import BytesIO


if "critical_constants" in st.session_state:
    if len(st.session_state.critical_constants) > 1:
        dew, bub = None, None
        model_setter = st.session_state.model_setter
        model_params = st.session_state.critical_constants

        model = st.session_state.model

        nc = len(model_params["Tc [K]"])
        t0 = model_params["Tc [K]"].mean()
        p0 = model_params["Pc [bar]"].mean()
        z = np.ones(nc)
        z = z/sum(z)

        c1, c2 = st.columns(2)
        with c1:

            c11, c12 = st.columns(2)
            with c11:
                st.subheader("Fluid composition (moles)")
                editor = st.data_editor(z, use_container_width=False)

                z = editor/sum(editor)
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
                dew = model.phase_envelope_pt(z, kind="dew", t0=t0, p0=0.1)
                bub = model.phase_envelope_pt(z, kind="bubble", t0=200, p0=p0)
        with c2:
            if dew and bub:
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=dew["T"],
                        y=dew["P"],
                        mode="lines",
                        name="Phase Envelope",
                    )
                )
                fig.add_trace(
                    go.Scatter(
                        x=bub["T"],
                        y=bub["P"],
                        mode="lines",
                        name="Phase Envelope",
                    )
                )

                fig.update_xaxes( title_text="Temperature [K]",)
                fig.update_yaxes( title_text="Pressure [bar]",)
                st.plotly_chart(fig, use_container_width=True, points=1000)

    else:
        st.warning("Please select a model and its parameters first.")
else:
    st.warning("Please select a model and its parameters first.")