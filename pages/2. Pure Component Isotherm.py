import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from settings import orchestra

orchestra.show_critical_constants()

model = st.session_state.model
nc = st.session_state.nc

which = st.selectbox("Number of component", options=[i + 1 for i in range(nc)])

resolution = st.number_input(
    "Resolution",
    min_value=1,
    value=1000,
    step=1,
)

temperature = st.number_input(
    "Temperature [K]",
    min_value=0.0,
    value=273.15,
    step=5.0,
)

ps = np.linspace(1e-1, 1000, resolution)
vs = np.array([model.volume([1], pressure=p, temperature=temperature) for p in ps])

fig = px.line(
    {"ps": ps, "vs": vs},
    x="vs",
    y="ps",
    labels={"x": "Volume [L/mol]", "y": "P [bar]"},
    title="Isotherm",
)

st.plotly_chart(fig, use_container_width=False)
