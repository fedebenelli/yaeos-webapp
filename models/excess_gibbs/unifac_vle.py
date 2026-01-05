from typing import Dict, List
import yaeos
from models.excess_gibbs.unifac_base import UNIFACBaseModel


class UNIFACVLEModel(UNIFACBaseModel):
    """Original UNIFAC VLE model"""

    def get_name(self) -> str:
        return "UNIFAC-VLE"

    def get_ge_object(self):
        """Returns: yaeos.UNIFACVLE(molecules)"""
        return yaeos.UNIFACVLE(self.molecules)

    def get_yaeos_object(self, config):
        return yaeos.UNIFACVLE(self.molecules)

    @classmethod
    def get_display_name(cls) -> str:
        return "UNIFAC-VLE (Original)"

    @classmethod
    def get_description(cls) -> str:
        return """
        Original UNIFAC model for vapor-liquid equilibrium.
        Requires functional group definitions for each component.
        
        **Example groups:**
        - Methanol: `15:1` (1 CH₃OH group)
        - Ethanol: `1:1, 2:1, 14:1` (1 CH₃, 1 CH₂, 1 OH)
        - Water: `16:1` (1 H₂O group)
        """

    @classmethod
    def _get_ugropy_module(cls):
        import ugropy

        return ugropy.unifac
