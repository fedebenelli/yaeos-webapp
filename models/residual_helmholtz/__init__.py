from models.residual_helmholtz.cubic.core import CEOSModelStrategy
from models.residual_helmholtz.cubic.srk import SoaveRedlichKwong
from models.residual_helmholtz.cubic.pr76 import PengRobinson76
from models.residual_helmholtz.cubic.pr78 import PengRobinson78
from models.residual_helmholtz.cubic.rkpr import RKPR
from models.residual_helmholtz.cubic.psrk import PSRK

CUBIC_EOS_REGISTRY = {
    "PengRobinson76": PengRobinson76,
    "PengRobinson78": PengRobinson78,
    "SoaveRedlichKwong": SoaveRedlichKwong,
    "RKPR": RKPR,
    "PSRK": PSRK,
}
