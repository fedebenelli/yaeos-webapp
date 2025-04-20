import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from settings import orchestra

orchestra.show_critical_constants()

model_setter = st.session_state.model_setter
model_params = st.session_state.critical_constants
which = st.selectbox(
    "Number of component",
    options=[i+1 for i in range(len(model_params))]
    )

temperature = st.number_input(
    "Temperature [K]",
    min_value=0.0,
    value=273.15,
    step=5.0,
)


Tc = [model_params["Tc"].values[which-1]]
Pc = [model_params["Tc"].values[which-1]]
w = [model_params["w"].values[which-1]]

model = model_setter(Tc, Pc, w)

ps = np.linspace(1e-1, 1000, 10000)
vs = [model.volume([1], pressure=p, temperature=temperature) for p in ps]

fig = px.line(
    {"ps": ps, "vs": vs},
    x="vs",
    y="ps",
    labels={"x": "Volume [L/mol]", "y": "P [bar]"},
    title="Isotherm",
)

st.plotly_chart(fig, use_container_width=False)