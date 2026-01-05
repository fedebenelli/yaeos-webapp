from typing import Dict, List
import yaeos
from models.excess_gibbs.unifac_base import UNIFACBaseModel


class UNIFACDortmundModel(UNIFACBaseModel):
    """UNIFAC Dortmund variant"""

    def get_name(self) -> str:
        return "UNIFAC-Dortmund"

    def get_ge_object(self):
        """Returns: yaeos.UNIFACDortmund(molecules)"""
        return yaeos.UNIFACDortmund(self.molecules)

    def get_yaeos_object(self, config):
        return yaeos.UNIFACDortmund(self.molecules)

    @classmethod
    def get_display_name(cls) -> str:
        return "UNIFAC-Dortmund"

    @classmethod
    def get_description(cls) -> str:
        return """
        Modified UNIFAC (Dortmund) with temperature-dependent parameters.
        Provides improved accuracy over the original UNIFAC model.
        
        **Features:**
        - Temperature-dependent group interaction parameters
        - Extended database with more functional groups
        - Better representation of strongly non-ideal systems
        """

    @classmethod
    def _get_ugropy_module(cls):
        import ugropy

        return ugropy.dortmund
