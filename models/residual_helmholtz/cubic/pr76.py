from models.residual_helmholtz.cubic.core import CEOSModelStrategy
from thermo_utils import ComponentData
from ui_components import input_basic_component_properties
from typing import List, Optional
import yaeos


class PengRobinson76(CEOSModelStrategy):
    @classmethod
    def get_display_name(cls) -> str:
        return "Peng-Robinson (1976)"

    @classmethod
    def get_description(cls) -> str:
        return "Classic Peng-Robinson equation of state (1976)"

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return []  # Only needs Tc, Pc, w

    @classmethod
    def requires_mixing_rule(cls) -> bool:
        return True

    @classmethod
    def setup_component_ui(cls, key_prefix: str = "comp") -> ComponentData:
        name, tc, pc, w = input_basic_component_properties(key_prefix)
        return ComponentData(name=name, tc=tc, pc=pc, w=w)

    @classmethod
    def get_bulk_import_format(cls) -> str:
        return """**Copy and paste from Excel with the following format:**
        
| Name | Tc [K] | Pc [bar] | ω |
|------|--------|----------|---|
| Component1 | 190.6 | 46.0 | 0.011 |
| Component2 | 305.3 | 48.7 | 0.099 |

Just copy the data rows from your Excel spreadsheet (including headers or not)."""

    @classmethod
    def get_bulk_import_example(cls) -> str:
        return """Name\tTc [K]\tPc [bar]\tω
Methane\t190.6\t46.0\t0.011
Ethane\t305.3\t48.7\t0.099
Propane\t369.8\t42.5\t0.152
n-Butane\t425.1\t37.9\t0.200
n-Pentane\t469.7\t33.7\t0.252"""

    @classmethod
    def parse_bulk_import_line(
        cls, parts: List[str], line_num: int
    ) -> tuple[Optional[ComponentData], Optional[str]]:
        if len(parts) < 4:
            return (
                None,
                f"Line {line_num}: Requires 4 columns (Name, Tc, Pc, ω), got {len(parts)}",
            )

        try:
            name = parts[0]
            tc = float(parts[1].replace(",", "."))
            pc = float(parts[2].replace(",", "."))
            w = float(parts[3].replace(",", "."))

            if tc <= 0 or pc <= 0:
                return None, f"Line {line_num}: Tc and Pc must be positive"

            return ComponentData(name=name, tc=tc, pc=pc, w=w), None
        except ValueError as e:
            return (
                None,
                f"Line {line_num}: Could not convert values to numbers - {str(e)}",
            )

    @classmethod
    def get_eos_object(cls, config):
        tc = [component.tc for component in config.components]
        pc = [component.pc for component in config.components]
        w = [component.w for component in config.components]
        mixrule = (
            config.mixing_rule.get_mixrule_object()
            if config.mixing_rule
            else None
        )

        print(config.mixing_rule)
        print(mixrule)

        return yaeos.PengRobinson76(
            critical_temperatures=tc,
            critical_pressures=pc,
            acentric_factors=w,
            mixrule=mixrule,
        )
