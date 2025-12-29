from models.residual_helmholtz.cubic.core import CEOSModelStrategy
from ui_components import input_basic_component_properties
from thermo_utils import ComponentData
from typing import List, Optional
import streamlit as st

import yaeos


class RKPR(CEOSModelStrategy):
    @classmethod
    def get_display_name(cls) -> str:
        return "RKPR"

    @classmethod
    def get_description(cls) -> str:
        return (
            "Redlich-Kwong-Peng-Robinson with additional flexibility parameter"
        )

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return ["zc"]  # Requires critical compressibility factor

    @classmethod
    def requires_mixing_rule(cls) -> bool:
        return True

    @classmethod
    def setup_component_ui(cls, key_prefix: str = "comp") -> ComponentData:
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            name = st.text_input(
                "Component Name", value="Component 1", key=f"{key_prefix}_name"
            )
        with col2:
            tc = st.number_input(
                "Tc [K]",
                value=190.6,
                min_value=0.0,
                step=10.0,
                key=f"{key_prefix}_tc",
            )
        with col3:
            pc = st.number_input(
                "Pc [bar]",
                value=46.0,
                min_value=0.0,
                step=1.0,
                key=f"{key_prefix}_pc",
            )
        with col4:
            w = st.number_input(
                "ω",
                value=0.011,
                min_value=0.0,
                step=0.001,
                format="%.3f",
                key=f"{key_prefix}_w",
            )
        with col5:
            zc = st.number_input(
                "Zc",
                value=0.29,
                min_value=0.0,
                max_value=1.0,
                step=0.01,
                format="%.3f",
                key=f"{key_prefix}_zc",
            )

        return ComponentData(name=name, tc=tc, pc=pc, w=w, zc=zc)

    @classmethod
    def get_bulk_import_format(cls) -> str:
        return """**Copy and paste from Excel with the following format for RKPR:**
        
| Name | Tc [K] | Pc [bar] | ω | Zc |
|------|--------|----------|---|----|
| Component1 | 190.6 | 46.0 | 0.011 | 0.29 |
| Component2 | 305.3 | 48.7 | 0.099 | 0.28 |"""

    @classmethod
    def get_bulk_import_example(cls) -> str:
        return """Name\tTc [K]\tPc [bar]\tω\tZc
Methane\t190.6\t46.0\t0.011\t0.288
Ethane\t305.3\t48.7\t0.099\t0.279
Propane\t369.8\t42.5\t0.152\t0.276"""

    @classmethod
    def parse_bulk_import_line(
        cls, parts: List[str], line_num: int
    ) -> tuple[Optional[ComponentData], Optional[str]]:
        if len(parts) < 5:
            return (
                None,
                f"Line {line_num}: RKPR requires 5 columns (Name, Tc, Pc, ω, Zc), got {len(parts)}",
            )

        try:
            name = parts[0]
            tc = float(parts[1].replace(",", "."))
            pc = float(parts[2].replace(",", "."))
            w = float(parts[3].replace(",", "."))
            zc = float(parts[4].replace(",", "."))

            if tc <= 0 or pc <= 0:
                return None, f"Line {line_num}: Tc and Pc must be positive"

            if not (0 < zc < 1):
                return None, f"Line {line_num}: Zc must be between 0 and 1"

            return ComponentData(name=name, tc=tc, pc=pc, w=w, zc=zc), None
        except ValueError as e:
            return (
                None,
                f"Line {line_num}: Could not convert values to numbers - {str(e)}",
            )

    def get_eos_object(cls, config):
        """Create the yaeos RKPR object from config"""
        tc = [c.tc for c in config.components]
        pc = [c.pc for c in config.components]
        w = [c.w for c in config.components]

        # RKPR specific parameter: Critical Compressibility Factor
        zc = [c.zc for c in config.components]

        mixrule = (
            config.mixing_rule.get_mixrule_object()
            if config.mixing_rule
            else None
        )

        return yaeos.RKPR(
            critical_temperatures=tc,
            critical_pressures=pc,
            acentric_factors=w,
            critical_z=zc,
            mixrule=mixrule,
        )
