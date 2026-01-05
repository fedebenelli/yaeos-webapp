from typing import Dict, List
import yaeos
from models.excess_gibbs.unifac_base import UNIFACBaseModel


class UNIFACPSRKModel(UNIFACBaseModel):
    """PSRK-UNIFAC model"""

    def get_name(self) -> str:
        return "UNIFAC-PSRK"

    def get_ge_object(self):
        """Returns: yaeos.UNIFACPSRK(molecules)"""
        return yaeos.UNIFACPSRK(self.molecules)

    def get_yaeos_object(self, config):
        return yaeos.UNIFACPSRK(self.molecules)

    @classmethod
    def get_display_name(cls) -> str:
        return "UNIFAC-PSRK"

    @classmethod
    def get_description(cls) -> str:
        return """
        PSRK variant of UNIFAC for use with the Predictive SRK equation of state.
        Uses modified group parameters optimized for high-pressure applications.
        
        **Note:** Group IDs may differ from original UNIFAC.
        """

    @classmethod
    def _get_ugropy_module(cls):
        import ugropy

        return ugropy.psrk
