from abc import ABC, abstractmethod
from typing import Any, Dict, List
import numpy as np
import streamlit as st
from ui_components import create_nrtl_matrices, create_parameter_matrix


class GEModelStrategy(ABC):
    """Abstract base class for excess Gibbs energy models"""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_ge_object(self):
        """Create the yaeos GE model object"""
        pass

    @classmethod
    @abstractmethod
    def setup_ui(
        cls, n_components: int, component_names: List[str], key_prefix: str
    ):
        """
        Display UI for parameter configuration and return instantiated GE model.

        Parameters
        ----------
        n_components : int
            Number of components in the system
        component_names : List[str]
            Names of the components
        key_prefix : str
            Unique prefix for Streamlit widget keys

        Returns
        -------
        GEModelStrategy
            Configured GE model instance
        """
        pass

    @classmethod
    @abstractmethod
    def get_display_name(cls) -> str:
        """Get the display name for UI"""
        pass

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Get a brief description of the GE model"""
        pass