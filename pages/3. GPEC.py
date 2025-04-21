import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from io import BytesIO


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
        print(critical_line)
        fig.add_scatter(
            x=critical_line[x_col],
            y=critical_line[y_col],
            mode="lines",
            name="Critical Line",
        )

    return fig


model_setter = st.session_state.model_setter
model_params = st.session_state.critical_constants

z0 = [1, 0]
zi = [0, 1]

model = st.session_state.model

a0 = 1 - 1e-3

pure_psat_1 = model.pure_saturation_pressures(1)
pure_psat_2 = model.pure_saturation_pressures(2)

critical_line_21 = model.critical_line(
    z0=z0, zi=zi,
    a0=a0, s=a0, ds0=-1e-3, max_points=5000)

critical_line_12 = model.critical_line(
    z0=z0, zi=zi,
    a0=1e-5, s=1e-10, ds0=1e-5, max_points=5000)

critical_line_hpll = model.critical_line(
    z0=z0, zi=zi,
    a0=0.5, s=np.log(2000), ds0=-1e-3,
    ns=4,
    max_points=5000)


c1, c2 = st.columns(2)

with c1:
    fig = get_fig(
        [pure_psat_1, pure_psat_2],
        [critical_line_21, critical_line_12, critical_line_hpll], "T", "P"
    )
    st.plotly_chart(fig, use_container_width=False)
with c2:
    fig = get_fig(
        [pure_psat_1, pure_psat_2],
        [critical_line_21, critical_line_12, critical_line_hpll], "a", "P"
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
    label="Download as Excel File", data=buffer.getvalue(), 
    file_name=file_name, mime="application/vnd.ms-excel")