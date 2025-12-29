from abc import ABC, abstractmethod
from typing import List, Optional
from thermo_utils import ComponentData


class CEOSModelStrategy(ABC):
    """Abstract base class for Cubic EoS models"""

    @classmethod
    @abstractmethod
    def get_display_name(cls) -> str:
        """Get the display name for UI"""
        pass

    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Get a brief description of the model"""
        pass

    @classmethod
    @abstractmethod
    def get_required_parameters(cls) -> List[str]:
        """Get list of required component parameters beyond Tc, Pc, w"""
        pass

    @classmethod
    @abstractmethod
    def requires_mixing_rule(cls) -> bool:
        """Whether this model requires a mixing rule"""
        pass

    @classmethod
    @abstractmethod
    def setup_component_ui(cls, key_prefix: str = "comp") -> ComponentData:
        """
        Display UI for component input and return ComponentData instance.

        Parameters
        ----------
        key_prefix : str
            Unique prefix for Streamlit widget keys

        Returns
        -------
        ComponentData
            Configured component data instance
        """
        pass

    @classmethod
    @abstractmethod
    def get_bulk_import_format(cls) -> str:
        """
        Get the format description for bulk import.

        Returns
        -------
        str
            Markdown formatted description of the expected format
        """
        pass

    @classmethod
    @abstractmethod
    def get_bulk_import_example(cls) -> str:
        """
        Get example data for bulk import.

        Returns
        -------
        str
            Tab-separated example data
        """
        pass

    @classmethod
    @abstractmethod
    def parse_bulk_import_line(
        cls, parts: List[str], line_num: int
    ) -> tuple[Optional[ComponentData], Optional[str]]:
        """
        Parse a single line from bulk import.

        Parameters
        ----------
        parts : List[str]
            Split parts of the line
        line_num : int
            Line number (for error messages)

        Returns
        -------
        tuple[Optional[ComponentData], Optional[str]]
            (ComponentData, None) if successful, (None, error_message) if failed
        """
        pass

    @classmethod
    @abstractmethod
    def get_eos_object(cls, config):
        """Create the yaeos EoS object"""
        pass
