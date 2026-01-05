from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MixingRuleStrategy(ABC):
    """Abstract base class for mixing rules"""

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """Get mixing rule parameters"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get mixing rule name"""
        pass

    @abstractmethod
    def get_mixrule_object(self):
        """Create the yaeos mixing rule object"""
        pass

    @classmethod
    @abstractmethod
    def setup_ui(cls, n_components: int, component_names: List[str], key_prefix: str):
        """
        Display UI for parameter configuration and return instantiated mixing rule.

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
        MixingRuleStrategy
            Configured mixing rule instance
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
        """Get a brief description of the mixing rule"""
        pass
