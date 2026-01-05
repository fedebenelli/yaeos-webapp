from models.excess_gibbs.core import GEModelStrategy
from models.excess_gibbs.nrtl import NRTLModel
from models.excess_gibbs.uniquac import UNIQUACStrategy as UNIQUACModel
from models.excess_gibbs.unifac_vle import UNIFACVLEModel
from models.excess_gibbs.unifac_psrk import UNIFACPSRKModel
from models.excess_gibbs.unifac_dortmund import UNIFACDortmundModel

GE_MODEL_REGISTRY = {
    "NRTL": NRTLModel,
    "UNIQUAC": UNIQUACModel,
    "UNIFAC-VLE": UNIFACVLEModel,
    "UNIFAC-PSRK": UNIFACPSRKModel,
    "UNIFAC-Dortmund": UNIFACDortmundModel,
}
