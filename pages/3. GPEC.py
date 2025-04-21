import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from io import BytesIO

model_setter = st.session_state.model_setter
model_params = st.session_state.critical_constants

z0 = [1, 0]
zi = [0, 1]

model = st.session_state.model

x20 = 1e-3
x10 = 1 - x20

pure_psat_1 = model.pure_saturation_pressures(1)
pure_psat_2 = model.pure_saturation_pressures(2)

critical_line = model.critical_line(
    z0=z0, zi=zi,
    a0=x10, s=x10, ds0=-1e-3, max_points=5000)

critical_line_hpll = model.critical_line(
    z0=z0, zi=zi,
    a0=0.5, s=np.log(2000), ds0=-1e-3,
    ns=4,
    max_points=5000)

fig = px.line(
    x=pure_psat_1["T"],
    y=pure_psat_1["P"],
    labels={"x": "T [K]", "y": "P [bar]"},
    title="Pure saturation pressure",
)

fig.add_scatter(
    x=pure_psat_2["T"],
    y=pure_psat_2["P"],
    mode="lines",
    name="Pure saturation pressure 2",
)

fig.add_scatter(
    x=critical_line["T"],
    y=critical_line["P"],
    mode="lines",
    name="Critical Line 2 -> 1",
)

fig.add_scatter(
    x=critical_line_hpll["T"],
    y=critical_line_hpll["P"],
    mode="lines",
    name="Critical Line LL",
)

st.plotly_chart(fig, use_container_width=False)

df_1 = pd.DataFrame(pure_psat_1)
df_2 = pd.DataFrame(pure_psat_2)
df_cl21 = pd.DataFrame(critical_line)
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