from typing import Any, Dict, List, Optional
import numpy as np
import streamlit as st
import yaeos
from models.residual_helmholtz.cubic.mixing_rules.core import (
    MixingRuleStrategy,
)
from ui_components import create_parameter_matrix, display_matrix_info


class QMRMixingRule(MixingRuleStrategy):
    """Quadratic mixing rule (QMR) - van der Waals"""

    def __init__(
        self,
        kij: Optional[np.ndarray] = None,
        lij: Optional[np.ndarray] = None,
    ):
        self.kij = kij
        if lij is None:
            self.lij = np.zeros_like(kij)
        else:
            self.lij = lij

    def get_params(self) -> Dict[str, Any]:
        return {
            "kij": self.kij.tolist() if self.kij is not None else None,
            "lij": self.lij.tolist() if self.lij is not None else None,
        }

    def get_name(self) -> str:
        return "QMR (Quadratic)"

    def get_mixrule_object(self):
        """Returns: yaeos.QMR(kij, lij)"""
        return yaeos.QMR(self.kij, self.lij)

    @classmethod
    def get_display_name(cls) -> str:
        return "QMR - Quadratic Mixing Rule"

    @classmethod
    def get_description(cls) -> str:
        return "Standard van der Waals mixing rules with binary interaction parameters"

    @classmethod
    def setup_ui(cls, n_components: int, component_names: List[str], key_prefix: str):
        st.subheader("QMR - Quadratic Mixing Rule Parameters")
        st.markdown(cls.get_description())

        # Create kij matrix
        display_matrix_info("kij", symmetric=True)
        kij_matrix = create_parameter_matrix(
            n_components=n_components,
            component_names=component_names,
            matrix_name="kij",
            default_value=0.0,
            symmetric=True,
            key_prefix=f"{key_prefix}_kij",
            help_text="Binary interaction parameters kij for attractive term",
        )

        # Optional lij matrix
        use_lij = st.checkbox(
            "Use lij parameters for repulsive term",
            help="Usually lij = 0 or lij = kij for most systems",
            key=f"{key_prefix}_use_lij",
        )

        lij_matrix = None
        if use_lij:
            st.markdown("---")

            # Option to auto-fill lij
            auto_fill = st.radio(
                "lij initialization",
                ["Manual input", "lij = kij", "lij = 0"],
                horizontal=True,
                key=f"{key_prefix}_lij_autofill",
            )

            if auto_fill == "Manual input":
                display_matrix_info("lij", symmetric=True)
                lij_matrix = create_parameter_matrix(
                    n_components=n_components,
                    component_names=component_names,
                    matrix_name="lij",
                    default_value=0.0,
                    symmetric=True,
                    key_prefix=f"{key_prefix}_lij",
                    help_text="Binary interaction parameters lij for repulsive term",
                )
            elif auto_fill == "lij = kij":
                lij_matrix = kij_matrix.copy()
                st.success("✓ lij automatically set equal to kij")
            else:  # lij = 0
                lij_matrix = np.zeros_like(kij_matrix)
                st.success("✓ lij set to zero matrix")

        return cls(kij=kij_matrix, lij=lij_matrix)
