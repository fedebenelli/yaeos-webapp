from models.residual_helmholtz.cubic.core import CEOSModelStrategy
from ui_components import input_basic_component_properties
from thermo_utils import ComponentData
from typing import List, Optional
import streamlit as st

from ugropy import psrk

import numpy as np

import yaeos


class PSRK(CEOSModelStrategy):
    @classmethod
    def get_display_name(cls) -> str:
        return "PSRK (Predictive SRK)"

    @classmethod
    def get_description(cls) -> str:
        return (
            "Predictive Soave-Redlich-Kwong with built-in UNIFAC mixing rules"
        )

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return [
            "groups",
            "c1",
            "c2",
            "c3",
        ]  # UNIFAC groups and Mathias-Copeman params

    @classmethod
    def requires_mixing_rule(cls) -> bool:
        return False  # Has built-in mixing rule

    @classmethod
    def setup_component_ui(cls, key_prefix: str = "comp") -> ComponentData:
        # Basic properties
        name, tc, pc, w = input_basic_component_properties(key_prefix)

        # Mathias-Copeman parameters
        st.write("**Mathias-Copeman Parameters (optional):**")
        col1, col2, col3 = st.columns(3)
        with col1:
            c1 = st.number_input(
                "c1",
                value=0.0,
                step=0.1,
                format="%.4f",
                key=f"{key_prefix}_c1",
            )
        with col2:
            c2 = st.number_input(
                "c2",
                value=0.0,
                step=0.1,
                format="%.4f",
                key=f"{key_prefix}_c2",
            )
        with col3:
            c3 = st.number_input(
                "c3",
                value=0.0,
                step=0.1,
                format="%.4f",
                key=f"{key_prefix}_c3",
            )

        # PSRK groups
        st.write("**PSRK Groups (required for PSRK):**")
        st.info(
            "Enter functional groups as group_id:count pairs separated by commas. Example: 1:2, 2:8"
        )

        with st.expander("Get help from ugropy"):
            molecule_name = st.text_input(
                "Molecule Name",
                value="",
                placeholder="e.g., n-Decane",
                key=f"{key_prefix}_molecule_name_help",
            )
            if molecule_name:
                try:
                    groups = psrk.get_groups(molecule_name)
                    st.write(f"**PSRK Groups for {molecule_name}:**")
                    st.write(f"{groups.subgroups_num}")
                except Exception as e:
                    st.error(f"Error retrieving PSRK groups: {str(e)}")

        groups_str = st.text_input(
            "Groups",
            value="",
            placeholder="e.g., 1:2, 2:8",
            help="Format: group_id:count, group_id:count",
            key=f"{key_prefix}_groups",
        )

        groups = None
        if groups_str:
            try:
                groups = {}
                for pair in groups_str.split(","):
                    group_id, count = pair.strip().split(":")
                    groups[int(group_id)] = int(count)
            except:
                st.warning(
                    "Invalid groups format. Use: group_id:count, group_id:count"
                )
                groups = None

        return ComponentData(
            name=name, tc=tc, pc=pc, w=w, c1=c1, c2=c2, c3=c3, groups=groups
        )

    @classmethod
    def get_bulk_import_format(cls) -> str:
        return """**Copy and paste from Excel with the following format for PSRK:**
        
| Name | Tc [K] | Pc [bar] | ω | c1 | c2 | c3 | Groups |
|------|--------|----------|---|----|----|----|----|
| Methane | 190.6 | 46.0 | 0.011 | 0.49 | 0.0 | 0.0 | 118:1 |
| n-Decane | 617.7 | 21.1 | 0.492 | 1.24 | -0.35 | 0.73 | 1:2,2:8 |

**Groups format:** Use group_id:count pairs, multiple groups separated by commas (no spaces)"""

    @classmethod
    def get_bulk_import_example(cls) -> str:
        return """Name\tTc [K]\tPc [bar]\tω\tc1\tc2\tc3\tGroups
Methane\t190.6\t46.0\t0.011\t0.49258\t0.0\t0.0\t118:1
n-Decane\t617.7\t21.1\t0.492328\t1.2407\t-0.34943\t0.7327\t1:2,2:8"""

    @classmethod
    def parse_bulk_import_line(
        cls, parts: List[str], line_num: int
    ) -> tuple[Optional[ComponentData], Optional[str]]:
        if len(parts) < 8:
            return (
                None,
                f"Line {line_num}: PSRK requires 8 columns (Name, Tc, Pc, ω, c1, c2, c3, Groups), got {len(parts)}",
            )

        try:
            name = parts[0]
            tc = float(parts[1].replace(",", "."))
            pc = float(parts[2].replace(",", "."))
            w = float(parts[3].replace(",", "."))
            c1 = float(parts[4].replace(",", "."))
            c2 = float(parts[5].replace(",", "."))
            c3 = float(parts[6].replace(",", "."))

            # Parse groups
            groups_str = parts[7]
            groups = {}
            try:
                for pair in groups_str.split(","):
                    group_id, count = pair.strip().split(":")
                    groups[int(group_id)] = int(count)
            except:
                return (
                    None,
                    f"Line {line_num}: Invalid groups format '{groups_str}'. Use group_id:count,group_id:count",
                )

            if tc <= 0 or pc <= 0:
                return None, f"Line {line_num}: Tc and Pc must be positive"

            return (
                ComponentData(
                    name=name,
                    tc=tc,
                    pc=pc,
                    w=w,
                    c1=c1,
                    c2=c2,
                    c3=c3,
                    groups=groups,
                ),
                None,
            )
        except ValueError as e:
            return (
                None,
                f"Line {line_num}: Could not convert values to numbers - {str(e)}",
            )

    @classmethod
    def get_eos_object(cls, config):
        """Create the yaeos PSRK object from config"""
        tc = np.array([c.tc for c in config.components])
        pc = np.array([c.pc for c in config.components])
        w =  np.array([c.w for c in config.components])

        # PSRK specific parameters
        c1 = np.array([c.c1 for c in config.components])
        c2 = np.array([c.c2 for c in config.components])
        c3 = np.array([c.c3 for c in config.components])

        # Functional groups (List of Dict[int, int])
        groups = [c.groups for c in config.components]

        if np.all(c1 == 0):
            c1 = None

        if np.all(c2 == 0):
            c2 = None

        if np.all(c3 == 0):
            c3 = None
        print(c1)

        return yaeos.PSRK(
            critical_temperatures=tc,
            critical_pressures=pc,
            acentric_factors=w,
            molecules=groups,
            c1=c1,
            c2=c2,
            c3=c3,
        )
