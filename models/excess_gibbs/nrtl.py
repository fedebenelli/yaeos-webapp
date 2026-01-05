from typing import Any, Dict, List
import numpy as np
import streamlit as st
from ui_components import create_nrtl_matrices
from models.excess_gibbs.core import GEModelStrategy


class NRTLModel(GEModelStrategy):
    """NRTL excess Gibbs energy model"""

    def __init__(self, aij: np.ndarray, bij: np.ndarray, cij: np.ndarray):
        self.aij = aij
        self.bij = bij
        self.cij = cij

    def get_name(self) -> str:
        return "NRTL"

    def get_params(self) -> Dict[str, Any]:
        return {
            "aij": self.aij.tolist(),
            "bij": self.bij.tolist(),
            "cij": self.cij.tolist(),
        }

    def get_ge_object(self):
        """Returns: yaeos.NRTL(aij, bij, cij)"""
        return {
            "type": "NRTL",
            "aij": self.aij,
            "bij": self.bij,
            "cij": self.cij,
        }

    @classmethod
    def get_display_name(cls) -> str:
        return "NRTL"

    @classmethod
    def get_description(cls) -> str:
        return r"""
            Non-Random Two-Liquid model: $\tau_{ij} = a_{ij} + \frac{b_{ij}}{T}$
        """

    @classmethod
    def setup_ui(cls, n_components: int, component_names: List[str], key_prefix: str):
        st.write(f"**{cls.get_display_name()} Parameters**")
        st.info(cls.get_description())

        aij, bij, cij = create_nrtl_matrices(
            n_components=n_components,
            component_names=component_names,
            key_prefix=key_prefix,
        )

        return cls(aij=aij, bij=bij, cij=cij)
