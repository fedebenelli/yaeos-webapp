from typing import Any, Dict, List, Optional
import numpy as np
import streamlit as st
from models.residual_helmholtz.cubic.mixing_rules.core import (
    MixingRuleStrategy,
)
from ui_components import create_parameter_matrix


class QMRTDMixingRule(MixingRuleStrategy):
    """Temperature-dependent quadratic mixing rule (QMRTD)"""

    def __init__(
        self,
        kij_0: np.ndarray,
        kij_inf: np.ndarray,
        Tref: np.ndarray,
        lij: Optional[np.ndarray] = None,
    ):
        self.kij_0 = kij_0
        self.kij_inf = kij_inf
        self.Tref = Tref
        self.lij = lij

    def get_params(self) -> Dict[str, Any]:
        return {
            "kij_0": self.kij_0.tolist(),
            "kij_inf": self.kij_inf.tolist(),
            "Tref": self.Tref.tolist(),
            "lij": self.lij.tolist() if self.lij is not None else None,
        }

    def get_name(self) -> str:
        return "QMRTD (Temperature-Dependent)"

    def get_mixrule_object(self):
        """Returns: yaeos.QMRTD(kij_0, kij_inf, Tref, lij)"""
        return {
            "type": "QMRTD",
            "kij_0": self.kij_0,
            "kij_inf": self.kij_inf,
            "Tref": self.Tref,
            "lij": self.lij,
        }

    @classmethod
    def get_display_name(cls) -> str:
        return "QMRTD - Temperature-Dependent Quadratic"

    @classmethod
    def get_description(cls) -> str:
        return (
            "kij varies with temperature: kij(T) = kij_0 + (kij_inf - kij_0) * T / Tref"
        )

    @classmethod
    def setup_ui(cls, n_components: int, component_names: List[str], key_prefix: str):
        st.subheader("QMRTD - Temperature-Dependent Quadratic Mixing Rule")
        st.markdown(cls.get_description())

        # kij at T=0
        st.write("**kij at low temperature (kij_0):**")
        kij_0 = create_parameter_matrix(
            n_components=n_components,
            component_names=component_names,
            matrix_name="kij_0",
            default_value=0.0,
            symmetric=True,
            key_prefix=f"{key_prefix}_kij0",
        )

        # kij at T=inf
        st.markdown("---")
        st.write("**kij at high temperature (kij_inf):**")
        kij_inf = create_parameter_matrix(
            n_components=n_components,
            component_names=component_names,
            matrix_name="kij_inf",
            default_value=0.0,
            symmetric=True,
            key_prefix=f"{key_prefix}_kijinf",
        )

        # Reference temperature
        st.markdown("---")
        st.write("**Reference temperature (Tref):**")
        Tref = create_parameter_matrix(
            n_components=n_components,
            component_names=component_names,
            matrix_name="Tref",
            default_value=300.0,
            symmetric=True,
            key_prefix=f"{key_prefix}_tref",
            help_text="Reference temperature for kij interpolation [K]",
        )

        # Optional lij
        use_lij = st.checkbox("Use lij parameters", key=f"{key_prefix}_use_lij")
        lij_matrix = None
        if use_lij:
            st.markdown("---")
            lij_matrix = create_parameter_matrix(
                n_components=n_components,
                component_names=component_names,
                matrix_name="lij",
                default_value=0.0,
                symmetric=True,
                key_prefix=f"{key_prefix}_lij",
            )

        return cls(kij_0=kij_0, kij_inf=kij_inf, Tref=Tref, lij=lij_matrix)
