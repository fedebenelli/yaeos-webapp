from models.residual_helmholtz.cubic.mixing_rules.core import (
    MixingRuleStrategy,
)
from models.residual_helmholtz.cubic.mixing_rules.qmrtd import QMRTDMixingRule
from models.residual_helmholtz.cubic.mixing_rules.hv import HVMixingRule
from models.residual_helmholtz.cubic.mixing_rules.hvnrtl import (
    HVNRTLMixingRule,
)
from models.residual_helmholtz.cubic.mixing_rules.mhv1 import MHVMixingRule
from models.residual_helmholtz.cubic.mixing_rules.qmr import QMRMixingRule

MIXING_RULE_REGISTRY = {
    "QMR": QMRMixingRule,
    "QMRTD": QMRTDMixingRule,
    "HV": HVMixingRule,
    "MHV": MHVMixingRule,
    "HVNRTL": HVNRTLMixingRule,
}
