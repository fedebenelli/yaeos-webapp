from models.excess_gibbs.core import GEModelStrategy
from models.excess_gibbs.nrtl import NRTLModel
from models.excess_gibbs.uniquac import UNIQUACStrategy

GE_MODEL_REGISTRY = {"NRTL": NRTLModel, "UNIQUAC": UNIQUACStrategy}
