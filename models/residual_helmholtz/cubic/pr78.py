from models.residual_helmholtz.cubic.core import CEOSModelStrategy
from models.residual_helmholtz.cubic.pr76 import PengRobinson76
from ui_components import input_basic_component_properties
from thermo_utils import ComponentData
from typing import List, Optional

import yaeos


class PengRobinson78(CEOSModelStrategy):
    @classmethod
    def get_display_name(cls) -> str:
        return "Peng-Robinson (1978)"

    @classmethod
    def get_description(cls) -> str:
        return "Modified Peng-Robinson equation with improved alpha function (1978)"

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return []

    @classmethod
    def requires_mixing_rule(cls) -> bool:
        return True

    @classmethod
    def setup_component_ui(cls, key_prefix: str = "comp") -> ComponentData:
        name, tc, pc, w = input_basic_component_properties(key_prefix)
        return ComponentData(name=name, tc=tc, pc=pc, w=w)

    @classmethod
    def get_bulk_import_format(cls) -> str:
        return PengRobinson76.get_bulk_import_format()

    @classmethod
    def get_bulk_import_example(cls) -> str:
        return PengRobinson76.get_bulk_import_example()

    @classmethod
    def parse_bulk_import_line(
        cls, parts: List[str], line_num: int
    ) -> tuple[Optional[ComponentData], Optional[str]]:
        return PengRobinson76.parse_bulk_import_line(parts, line_num)

    def get_eos_object(cls, config):
        """Create the yaeos PengRobinson78 object from config"""
        tc = [c.tc for c in config.components]
        pc = [c.pc for c in config.components]
        w = [c.w for c in config.components]

        mixrule = (
            config.mixing_rule.get_mixrule_object()
            if config.mixing_rule
            else None
        )

        return yaeos.PengRobinson78(
            critical_temperatures=tc,
            critical_pressures=pc,
            acentric_factors=w,
            mixrule=mixrule,
        )
