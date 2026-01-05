from typing import Any, Dict, List
import streamlit as st
from models.residual_helmholtz.cubic.mixing_rules.core import (
    MixingRuleStrategy,
)
from models.excess_gibbs import GEModelStrategy, GE_MODEL_REGISTRY


class MHVMixingRule(MixingRuleStrategy):
    """Modified Huron-Vidal (MHV1) mixing rule with GE model"""

    def __init__(self, ge_model: "GEModelStrategy", q: float = -0.53):
        self.ge_model = ge_model
        self.q = q

    def get_params(self) -> Dict[str, Any]:
        return {
            "ge_model": self.ge_model.get_name(),
            "q": self.q,
            **self.ge_model.get_params(),
        }

    def get_name(self) -> str:
        return f"MHV ({self.ge_model.get_name()})"

    def get_mixrule_object(self):
        """Returns: yaeos.MHV(ge=ge_model, q=q)"""
        return {
            "type": "MHV",
            "ge": self.ge_model.get_ge_object(),
            "q": self.q,
        }

    @classmethod
    def get_display_name(cls) -> str:
        return "MHV - Modified Huron-Vidal"

    @classmethod
    def get_description(cls) -> str:
        return "Modified Huron-Vidal mixing rule with excess Gibbs energy model and q parameter"

    @classmethod
    def setup_ui(
        cls, n_components: int, component_names: List[str], key_prefix: str
    ):
        st.subheader("MHV - Mixing Rule with Excess Gibbs Model")
        st.markdown(cls.get_description())

        # Select GE model from registry
        ge_model_options = {
            key: ge_cls.get_display_name()
            for key, ge_cls in GE_MODEL_REGISTRY.items()
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

        st.markdown("---")
        q_param = st.number_input(
            "q parameter",
            value=-0.53,
            step=0.01,
            format="%.3f",
            help="MHV q parameter (typically -0.53 for PR, -0.593 for SRK)",
            key=f"{key_prefix}_q",
        )

        return cls(ge_model=ge_model, q=q_param)
