import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import json
import yaeos
from thermo_utils import ComponentData
from gpec import show_gpec_diagram
from home import show_home_page
from phase_envelope import show_phase_envelope
from model_setup import show_model_configuration

from ui_components import (
    create_parameter_matrix,
    display_matrix_info,
    create_nrtl_matrices,
)

from models.excess_gibbs import GE_MODEL_REGISTRY, GEModelStrategy
from models.residual_helmholtz.cubic.mixing_rules import (
    MIXING_RULE_REGISTRY,
    MixingRuleStrategy,
)
from models.residual_helmholtz import CUBIC_EOS_REGISTRY, CEOSModelStrategy

from models import ModelType


# ==============================================================================
# Model Configuration Manager
# ==============================================================================
class EOSModelConfig:
    """Configuration manager for equation of state models"""

    def __init__(self):
        self.components: List[ComponentData] = []
        self.model_category: str = ModelType.RESIDUAL_HELMHOLTZ  # ArModel or GeModel
        self.model_type: str = "PengRobinson76"  # Specific model within category
        self.mixing_rule: Optional[MixingRuleStrategy] = None

    def add_component(self, component: ComponentData):
        self.components.append(component)

    def set_mixing_rule(self, mixing_rule: MixingRuleStrategy):
        self.mixing_rule = mixing_rule

    def is_ar_model(self) -> bool:
        """Check if current configuration is for ArModel"""
        return self.model_category == ModelType.RESIDUAL_HELMHOLTZ

    def is_ge_model(self) -> bool:
        """Check if current configuration is for GeModel"""
        return self.model_category == ModelType.EXCESS_GIBBS

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary"""
        config_dict = {
            "model_category": self.model_category,
            "model_type": self.model_type,
            "components": [
                {"name": c.name, "tc": c.tc, "pc": c.pc, "w": c.w}
                for c in self.components
            ],
        }
        
        if self.is_ar_model():
            config_dict["mixing_rule"] = (
                self.mixing_rule.get_name() if self.mixing_rule else None
            )
            config_dict["mixing_params"] = (
                self.mixing_rule.get_params() if self.mixing_rule else None
            )
        
        return config_dict


# ==============================================================================
# Streamlit App Pages
# ==============================================================================
def main():
    st.set_page_config(
        page_title="YAEOS Web App", layout="wide", page_icon="🧪"
    )

    # Initialize session state
    if "model_config" not in st.session_state:
        st.session_state.model_config = EOSModelConfig()
    if "model_created" not in st.session_state:
        st.session_state.model_created = False

    # Sidebar navigation
    st.sidebar.title("🧪 YAEOS")
    st.sidebar.markdown("*Thermodynamic Equation of State Calculator*")

    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Model Configuration", "Phase Envelope", "GPEC Diagram"],
    )

    if page == "Home":
        show_home_page()
    elif page == "Model Configuration":
        show_model_configuration()
    elif page == "Phase Envelope":
        show_phase_envelope()
    elif page == "GPEC Diagram":
        show_gpec_diagram()

if __name__ == "__main__":
    main()
