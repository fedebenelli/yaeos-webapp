import numpy as np
import streamlit as st
import yaeos
from typing import List, Dict, Any, Optional
from models.excess_gibbs import GEModelStrategy
from ui_components import create_parameter_matrix, display_matrix_info


class UNIQUACStrategy(GEModelStrategy):
    """
    Strategy for the UNIQUAC Excess Gibbs Energy model.
    Reflects the full parameter set defined in yaeos.models.excess_gibbs.UNIQUAC.
    """

    def __init__(
        self,
        qs: np.ndarray,
        rs: np.ndarray,
        aij: Optional[np.ndarray] = None,
        bij: Optional[np.ndarray] = None,
        cij: Optional[np.ndarray] = None,
        dij: Optional[np.ndarray] = None,
        eij: Optional[np.ndarray] = None,
    ):
        self.qs = qs
        self.rs = rs
        self.aij = aij
        self.bij = bij
        self.cij = cij
        self.dij = dij
        self.eij = eij

    @classmethod
    def get_display_name(cls) -> str:
        return "UNIQUAC"

    @classmethod
    def get_name(cls) -> str:
        return "UNIQUAC"

    @classmethod
    def get_description(cls) -> str:
        return {
            "Name": (
                "Universal Quasi-Chemical model with full interaction "
                "parameter support (aij...eij)."
            ),
            "$q$": "Surface area parameters for each component.",
            "$r$": "Volume parameters for each component.",
            "$a_{ij}$": "Matrix of interaction parameters aij.",
            "$b_{ij}$": "Matrix of interaction parameters bij.",
            "$c_{ij}$": "Matrix of interaction parameters cij.",
            "$d_{ij}$": "Matrix of interaction parameters dij.",
            "$e_{ij}$": "Matrix of interaction parameters eij.",
            "General Form": r"$\frac{G^E}{RT} = \sum_k n_k \ln\frac{\phi_k}{x_k} + \frac{z}{2}\sum_k q_k n_k \ln\frac{\theta_k}{\phi_k} - \sum_k q_k n_k \ln\left(\sum_l \theta_l \tau_{lk} \right)$",
            "$x_k$": r"$\frac{n_k}{\sum_l n_l}$",
            r"$\phi_k$": r"$\frac{r_k n_k}{\sum_l r_l n_l}$",
            r"$\theta_k$": r"$\frac{q_k n_k}{\sum_l q_l n_l}$",
            r"$\tau_{lk}$": r"$\exp\left[\frac{-\Delta U_{lk}}{RT} \right]$",
            r"$-\frac{\Delta U_{lk}}{RT}$": r"$a_{lk}+\frac{b_{lk}}{T}+c_{lk}\ln T + d_{lk}T + e_{lk}{T^2}$",
        }

    def get_params(self) -> Dict[str, Any]:
        """Return parameters in a serializable format."""
        return {
            "qs": self.qs.tolist(),
            "rs": self.rs.tolist(),
            "aij": self.aij.tolist() if self.aij is not None else None,
            "bij": self.bij.tolist() if self.bij is not None else None,
            "cij": self.cij.tolist() if self.cij is not None else None,
            "dij": self.dij.tolist() if self.dij is not None else None,
            "eij": self.eij.tolist() if self.eij is not None else None,
        }

    def get_ge_object(self) -> yaeos.UNIQUAC:
        """
        Factory method to create the actual yaeos.UNIQUAC object.
        Analogous to PengRobinson76.get_eos_object, but for GE models.
        """
        return yaeos.UNIQUAC(
            qs=self.qs,
            rs=self.rs,
            aij=self.aij,
            bij=self.bij,
            cij=self.cij,
            dij=self.dij,
            eij=self.eij,
        )

    @classmethod
    def setup_ui(
        cls, n_components: int, component_names: List[str], key_prefix: str
    ) -> "UNIQUACStrategy":
        """
        Configures the UI to accept all UNIQUAC parameters defined in yaeos.txt.
        """
        st.markdown(f"**{cls.get_display_name()} Configuration**")

        with st.expander("Model Description", expanded=False):
            desc = cls.get_description()
            for key, val in desc.items():
                st.markdown(f"**{key}:** {val}")

        # 1. Structural Parameters (qs, rs)
        st.write("###### Structural Parameters")
        col1, col2 = st.columns(2)

        rs = []
        qs = []

        with col1:
            st.write("$r_i$ (Volume Parameter)")
            for i, name in enumerate(component_names):
                val = st.number_input(
                    f"r for {name}", value=1.0, step=0.1, key=f"{key_prefix}_r_{i}"
                )
                rs.append(val)

        with col2:
            st.write("$q_i$ (Surface Area Parameter)")
            for i, name in enumerate(component_names):
                val = st.number_input(
                    f"q for {name}", value=1.0, step=0.1, key=f"{key_prefix}_q_{i}"
                )
                qs.append(val)

        rs_arr = np.array(rs)
        qs_arr = np.array(qs)

        # 2. Interaction Parameters (Matrices)
        st.write("###### Interaction Parameters")
        st.info(
            r"Parameters correspond to the expansion: $\frac{-\Delta U_{ij}}{RT} = a_{ij} + b_{ij}/T + c_{ij} \ln(T) + d_{ij} T + e_{ij}/T^2$"
        )

        tabs = st.tabs(["aij", "bij", "cij", "dij", "eij"])

        # Helper to create optional matrix inputs
        def get_matrix(tab, name, default=0.0):
            with tab:
                # We use a checkbox to enable/disable specific matrices to keep UI clean
                # unless it's 'aij' or 'bij' which are common.
                use_matrix = True
                if name not in ["aij", "bij"]:
                    use_matrix = st.checkbox(
                        f"Include {name} parameters?", key=f"{key_prefix}_use_{name}"
                    )

                if use_matrix:
                    display_matrix_info(name, symmetric=False)
                    return create_parameter_matrix(
                        n_components,
                        component_names,
                        name,
                        default_value=default,
                        symmetric=False,
                        key_prefix=f"{key_prefix}_{name}",
                    )
                return None

        aij_mat = get_matrix(tabs[0], "aij")
        bij_mat = get_matrix(tabs[1], "bij")
        cij_mat = get_matrix(tabs[2], "cij")
        dij_mat = get_matrix(tabs[3], "dij")
        eij_mat = get_matrix(tabs[4], "eij")

        return cls(
            qs=qs_arr,
            rs=rs_arr,
            aij=aij_mat,
            bij=bij_mat,
            cij=cij_mat,
            dij=dij_mat,
            eij=eij_mat,
        )
