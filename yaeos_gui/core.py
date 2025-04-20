import gradio as gr
import numpy as np
import plotly.graph_objects as go
from yaeos import SoaveRedlichKwong, PengRobinson76

from yaeos_gui.interfaces.main import interface as main

models = {
    "PengRobinson76": PengRobinson76,
    "SoaveRedlichKwong": SoaveRedlichKwong,
}


gr.TabbedInterface([main])