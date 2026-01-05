from typing import Any, Dict, List, Optional
import streamlit as st
from models.excess_gibbs.core import GEModelStrategy
from thermo_utils import ComponentData


def ugropy_helper(cls, name: str, key_prefix: str, i: int):
    molecule_name = name

    if molecule_name and st.button(
        "Search", key=f"{key_prefix}_ugropy_btn_{i}"
    ):
        try:
            import ugropy

            ug_c1, ug_c2 = st.columns(2)
            model_module = cls._get_ugropy_module()
            groups = model_module.get_groups(molecule_name)
            with ug_c1:
                st.success(f"Found groups for {molecule_name}:")
                st.json(groups.subgroups_num)
                groups_str = ",".join(
                    [
                        f"{gid}:{cnt}"
                        for gid, cnt in groups.subgroups_num.items()
                    ]
                )
                st.code("Copy and paste below:\n" + groups_str, language=None)
            with ug_c2:
                st.info("Molecule Structure:")
                svg_string = groups.draw().data
                st.image(svg_string, caption="Local SVG", width=300)
        except ImportError:
            st.error("ugropy not installed. Run: pip install ugropy")
        except Exception as e:
            st.warning(f"Could not find groups: {str(e)}")
        return groups, groups_str
    return None, None


class UNIFACBaseModel(GEModelStrategy):
    """Base class for UNIFAC-type models"""

    def __init__(self, molecules: List[Dict[int, int]]):
        self.molecules = molecules

    def get_params(self) -> Dict[str, Any]:
        return {"molecules": self.molecules}

    @classmethod
    def setup_ui(
        cls, n_components: int, component_names: List[str], key_prefix: str
    ):
        st.write(f"**{cls.get_display_name()} Parameters**")
        st.info(cls.get_description())

        molecules = []

        for i, name in enumerate(component_names):
            st.markdown(f"**Component {i+1}: {name}**")

            with st.expander(f"🔍 Get groups using ugropy for {name}"):
                groups_str, groups_str = ugropy_helper(
                    cls, name, key_prefix, i
                )

            groups_str = st.text_input(
                f"Groups for {name}",
                value=groups_str if groups_str else "",
                placeholder="e.g., 1:2, 2:1, 14:1",
                help="Format: group_id:count, group_id:count",
                key=f"{key_prefix}_groups_{i}",
            )

            groups = {}
            if groups_str:
                try:
                    for pair in groups_str.split(","):
                        group_id, count = pair.strip().split(":")
                        groups[int(group_id)] = int(count)
                except:
                    st.error(
                        f"Invalid format for {name}. Use: group_id:count, group_id:count"
                    )
                    groups = {}

            if not groups:
                st.warning(f"⚠️ No groups specified for {name}")

            molecules.append(groups)
            st.markdown("---")

        # Validate all components have groups
        if all(mol for mol in molecules):
            st.success("✅ All components have functional groups defined")
        else:
            st.error("❌ Please specify functional groups for all components")

        return cls(molecules=molecules)

    @classmethod
    def setup_component_ui(cls, key_prefix: str = "comp") -> ComponentData:
        """
        Default component setup for GeModels.
        Most GeModels (NRTL, UNIQUAC) only need basic properties (Tc, Pc, w).
        Models requiring groups (UNIFAC, PSRK) should override this method.
        """
        # Default behavior: Use the standard input function
        name = st.text_input(f"{key_prefix}_name", "Component Name")
        tc, pc, w = None, None, None
        # groups, _ = ugropy_helper(cls, name, key_prefix, 0)

        # Return standard component data
        return ComponentData(name=name, tc=tc, pc=pc, w=w)

    @classmethod
    def _get_ugropy_module(cls):
        """Override in subclasses to return correct ugropy module"""
        raise NotImplementedError
