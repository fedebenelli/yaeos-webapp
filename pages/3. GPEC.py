import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

model_setter = st.session_state.model_setter
model_params = st.session_state.critical_constants

z0 = [1, 0]
zi = [0, 1]

Tc = model_params["Tc"].values
Pc = model_params["Tc"].values
w = model_params["w"].values

model = model_setter(Tc, Pc, w)

pure_psat_1 = model.pure_saturation_pressures(1)
pure_psat_2 = model.pure_saturation_pressures(2)

critical_line = model.critical_line(
    z0=z0, zi=zi,
    a0=0.999, s=0.999, ds0=-1e-2, max_points=5000)

critical_line_hpll = model.critical_line(
    z0=z0, zi=zi,
    a0=0.5, s=np.log(2000), ds0=-1e-2,
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
    name="Critical Line 2 -> 1",
)

st.plotly_chart(fig, use_container_width=False)