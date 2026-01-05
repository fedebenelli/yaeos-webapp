from typing import Any, Dict, List
import streamlit as st
from models.residual_helmholtz.cubic.mixing_rules.core import (
    MixingRuleStrategy,
)
from models.excess_gibbs import GE_MODEL_REGISTRY


class HVMixingRule(MixingRuleStrategy):
    """Huron-Vidal mixing rule with GE model"""

    def __init__(self, ge_model: "GEModelStrategy"):
        self.ge_model = ge_model

    def get_params(self) -> Dict[str, Any]:
        return {
            "ge_model": self.ge_model.get_name(),
            **self.ge_model.get_params(),
        }

    def get_name(self) -> str:
        return f"HV ({self.ge_model.get_name()})"

    def get_mixrule_object(self):
        """Returns: yaeos.HV(ge=ge_model)"""
        return {"type": "HV", "ge": self.ge_model.get_ge_object()}

    @classmethod
    def get_display_name(cls) -> str:
        return "HV - Huron-Vidal"

    @classmethod
    def get_description(cls) -> str:
        return "Huron-Vidal mixing rule with excess Gibbs energy model"

    @classmethod
    def setup_ui(cls, n_components: int, component_names: List[str], key_prefix: str):
        st.subheader("HV - Mixing Rule with Excess Gibbs Model")
        st.markdown(cls.get_description())

        # Select GE model from registry
        ge_model_options = {
            key: ge_cls.get_display_name() for key, ge_cls in GE_MODEL_REGISTRY.items()
        }

        ge_model_type = st.selectbox(
            "Excess Gibbs Energy Model",
            list(ge_model_options.keys()),
            format_func=lambda x: ge_model_options[x],
            help="Select the GE model to use with the mixing rule",
            key=f"{key_prefix}_ge_type",
        )

        # Get the selected GE model class and instantiate it
        GEModelClass = GE_MODEL_REGISTRY[ge_model_type]
        ge_model = GEModelClass.setup_ui(
            n_components=n_components,
            component_names=component_names,
            key_prefix=f"{key_prefix}_{ge_model_type.lower()}",
        )

        return cls(ge_model=ge_model)
