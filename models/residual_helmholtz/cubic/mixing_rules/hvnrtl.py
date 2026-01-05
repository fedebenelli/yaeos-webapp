from typing import Any, Dict, List
import numpy as np
import streamlit as st
from models.residual_helmholtz.cubic.mixing_rules.core import (
    MixingRuleStrategy,
)
from ui_components import create_parameter_matrix


class HVNRTLMixingRule(MixingRuleStrategy):
    """Huron-Vidal with NRTL (HVNRTL) - special implementation"""

    def __init__(
        self,
        alpha: np.ndarray,
        gji: np.ndarray,
        use_kij: np.ndarray,
        kij: np.ndarray,
    ):
        self.alpha = alpha
        self.gji = gji
        self.use_kij = use_kij
        self.kij = kij

    def get_params(self) -> Dict[str, Any]:
        return {
            "alpha": self.alpha.tolist(),
            "gji": self.gji.tolist(),
            "use_kij": self.use_kij.tolist(),
            "kij": self.kij.tolist(),
        }

    def get_name(self) -> str:
        return "HVNRTL"

    def get_mixrule_object(self):
        """Returns: yaeos.HVNRTL(alpha, gji, use_kij, kij)"""
        return {
            "type": "HVNRTL",
            "alpha": self.alpha,
            "gji": self.gji,
            "use_kij": self.use_kij,
            "kij": self.kij,
        }

    @classmethod
    def get_display_name(cls) -> str:
        return "HVNRTL - Huron-Vidal with NRTL"

    @classmethod
    def get_description(cls) -> str:
        return "Special implementation combining HV and NRTL with selective kij usage"

    @classmethod
    def setup_ui(
        cls, n_components: int, component_names: List[str], key_prefix: str
    ):
        st.subheader("HVNRTL - Huron-Vidal with NRTL")
        st.markdown(cls.get_description())

        # Alpha parameters (symmetric)
        st.write("**Non-randomness parameter (alpha):**")
        alpha = create_parameter_matrix(
            n_components=n_components,
            component_names=component_names,
            matrix_name="alpha",
            default_value=0.3,
            symmetric=True,
            key_prefix=f"{key_prefix}_alpha",
        )

        # gji parameters (non-symmetric)
        st.markdown("---")
        st.write("**Energy parameters (gji) [K]:**")
        gji = create_parameter_matrix(
            n_components=n_components,
            component_names=component_names,
            matrix_name="gji",
            default_value=0.0,
            symmetric=False,
            key_prefix=f"{key_prefix}_gji",
        )

        # use_kij matrix (boolean)
        st.markdown("---")
        st.write("**Use kij flags (True/False):**")
        st.info("Specify which binary pairs should use kij corrections")

        use_kij = np.full((n_components, n_components), False)
        kij = np.zeros((n_components, n_components))

        for i in range(n_components):
            for j in range(i + 1, n_components):
                col1, col2 = st.columns([3, 1])
                with col1:
                    use_kij_val = st.checkbox(
                        f"Use kij for {component_names[i]}-{component_names[j]}",
                        key=f"{key_prefix}_use_kij_{i}_{j}",
                    )
                    use_kij[i, j] = use_kij_val
                    use_kij[j, i] = use_kij_val

                with col2:
                    if use_kij_val:
                        kij_val = st.number_input(
                            "kij",
                            value=0.0,
                            step=0.01,
                            format="%.4f",
                            key=f"{key_prefix}_kij_{i}_{j}",
                        )
                        kij[i, j] = kij_val
                        kij[j, i] = kij_val

        return cls(alpha=alpha, gji=gji, use_kij=use_kij, kij=kij)
