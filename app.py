import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import json
import yaeos
from thermo_utils import ComponentData

from ui_components import (
    create_parameter_matrix,
    display_matrix_info,
    create_nrtl_matrices,
)

from models.excess_gibbs import GE_MODEL_REGISTRY, GEModelStrategy
from models.residual_helmholtz.cubic.mixing_rules import (
    MIXING_RULE_REGISTRY,
    MixingRuleStrategy,
)
from models.residual_helmholtz import CUBIC_EOS_REGISTRY, CEOSModelStrategy


# ==============================================================================
# FACTORY PATTERN REGISTRY SYSTEM
# ==============================================================================
# This application uses the Factory Pattern with registries for extensibility.
#
# To add a new model/mixing rule/GE model:
# 1. Create a class inheriting from the appropriate base class
# 2. Implement required methods (especially setup_ui for UI configuration)
# 3. Add the class to the corresponding registry dictionary
#
# Registries:
# - CUBIC_EOS_REGISTRY: Cubic equations of state models
# - MIXING_RULE_REGISTRY: Mixing rules for cubic EoS
# - GE_MODEL_REGISTRY: Excess Gibbs energy models (used by some mixing rules)
# ==============================================================================


# ==============================================================================
# Model Configuration Manager
# ==============================================================================
class EOSModelConfig:
    """Configuration manager for equation of state models"""

    def __init__(self):
        self.components: List[ComponentData] = []
        self.model_type: str = "PengRobinson76"
        self.mixing_rule: Optional[MixingRuleStrategy] = None

    def add_component(self, component: ComponentData):
        self.components.append(component)

    def set_mixing_rule(self, mixing_rule: MixingRuleStrategy):
        self.mixing_rule = mixing_rule

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration to dictionary"""
        return {
            "model_type": self.model_type,
            "components": [
                {"name": c.name, "tc": c.tc, "pc": c.pc, "w": c.w}
                for c in self.components
            ],
            "mixing_rule": (self.mixing_rule.get_name() if self.mixing_rule else None),
            "mixing_params": (
                self.mixing_rule.get_params() if self.mixing_rule else None
            ),
        }

    def set_yaeos_model(self):
        """Create and set the yaeos model based on current configuration"""
        pass


# ==============================================================================
# Streamlit App Pages
# ==============================================================================
def main():
    st.set_page_config(page_title="YAEOS Web App", layout="wide", page_icon="🧪")

    # Initialize session state
    if "model_config" not in st.session_state:
        st.session_state.model_config = EOSModelConfig()
    if "model_created" not in st.session_state:
        st.session_state.model_created = False

    # Sidebar navigation
    st.sidebar.title("🧪 YAEOS")
    st.sidebar.markdown("*Thermodynamic Equation of State Calculator*")

    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Model Configuration", "Phase Envelope", "GPEC Diagram"],
    )

    if page == "Home":
        show_home_page()
    elif page == "Model Configuration":
        show_model_configuration()
    elif page == "Phase Envelope":
        show_phase_envelope()
    elif page == "GPEC Diagram":
        show_gpec_diagram()


def show_home_page():
    """Display home page with general information"""
    st.title("Welcome to YAEOS Web Interface")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("What is YAEOS?")
        st.markdown(
            """
        YAEOS is a Fortran library with Python bindings for thermodynamic calculations using 
        Equations of State (EoS). This web interface provides an intuitive way to:
        
        - Configure thermodynamic models (Cubic EoS, GERG-2008, etc.)
        - Perform phase equilibrium calculations
        - Generate phase envelopes and GPEC diagrams
        - Analyze binary and multicomponent systems
        """
        )

        st.header("Available Models")
        st.markdown(
            """
        **Cubic Equations of State:**
        - Peng-Robinson (1976, 1978)
        - Soave-Redlich-Kwong (SRK)
        - RKPR (Redlich-Kwong-Peng-Robinson)
        - PSRK (Predictive SRK)
        
        **Mixing Rules:**
        - Quadratic (van der Waals) with binary interaction parameters
        - Modified Huron-Vidal (MHV) with activity coefficient models
        - Wong-Sandler (WS)
        
        **Activity Coefficient Models (for advanced mixing rules):**
        - NRTL
        - UNIQUAC
        - UNIFAC variants
        """
        )

    with col2:
        st.header("Quick Start")
        st.info(
            """
        **Step 1:** Configure your model in the "Model Configuration" page
        
        **Step 2:** Add components with their properties (Tc, Pc, ω)
        
        **Step 3:** Select mixing rule and parameters
        
        **Step 4:** Run calculations in Phase Envelope or GPEC pages
        """
        )

        st.success(
            """
        💡 **Tip:** Start with a binary system using quadratic mixing rules 
        for easier configuration!
        """
        )

    st.markdown("---")
    st.header("Features Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Phase Envelope Calculations")
        st.markdown(
            """
        Calculate phase envelopes starting from dew or bubble points:
        - Pressure-Temperature (PT) diagrams
        - Visualize vapor-liquid equilibrium boundaries
        - Export calculation results
        """
        )

    with col2:
        st.subheader("📈 GPEC Diagrams")
        st.markdown(
            """
        Global Phase Equilibrium Calculations for binary systems:
        - Pressure-composition (Pxy) diagrams at constant T
        - Temperature-composition (Txy) diagrams at constant P
        - Critical locus visualization
        """
        )


def show_model_configuration():
    """Model configuration page"""
    st.title("Model Configuration")
    st.markdown("Configure your thermodynamic model, components, and mixing rules")
    st.markdown("---")

    config = st.session_state.model_config

    # Model Type Selection
    st.header("1. Select Model Type")

    # Build model options from registry
    model_options = {
        key: cls.get_display_name() for key, cls in CUBIC_EOS_REGISTRY.items()
    }

    config.model_type = st.selectbox(
        "Cubic EoS Model",
        list(model_options.keys()),
        format_func=lambda x: model_options[x],
        help="Select the cubic equation of state model",
    )

    # Get the selected model class
    ModelClass = CUBIC_EOS_REGISTRY[config.model_type]

    # Display model description
    st.info(f"ℹ️ {ModelClass.get_description()}")

    # Show required parameters info
    required_params = ModelClass.get_required_parameters()
    if required_params:
        param_names = ", ".join(required_params)
        st.warning(f"⚠️ This model requires additional parameters: {param_names}")

    st.markdown("---")

    # Component Configuration
    st.header("2. Add Components")

    col1, col2 = st.columns([3, 1], gap="small")

    with col1:
        st.subheader("Current Components")
        if config.components:
            for i, comp in enumerate(config.components):
                comp_info = (
                    f"{i+1}. {comp.name}: Tc={comp.tc}K, Pc={comp.pc}bar, ω={comp.w}"
                )

                # Add model-specific parameters if present
                if comp.zc is not None:
                    comp_info += f", Zc={comp.zc}"
                if comp.c1 is not None or comp.c2 is not None or comp.c3 is not None:
                    comp_info += f", c=[{comp.c1}, {comp.c2}, {comp.c3}]"
                if comp.groups:
                    groups_str = ",".join(
                        [f"{gid}:{cnt}" for gid, cnt in comp.groups.items()]
                    )
                    comp_info += f", Groups={{{groups_str}}}"

                st.text(comp_info)
        else:
            st.info("No components added yet")

    with col2:
        if st.button("Clear All", type="secondary"):
            config.components = []
            st.rerun()

    st.subheader("Add New Component")

    # Get the selected model class
    ModelClass = CUBIC_EOS_REGISTRY[config.model_type]

    # Call the model's setup_component_ui method
    new_comp = ModelClass.setup_component_ui(key_prefix="add_comp")

    if st.button("Add Component", type="primary"):
        config.add_component(new_comp)
        st.success(f"Added {new_comp.name}")
        st.rerun()

    # Common components database
    with st.expander("📚 Common Components Database"):
        common_components = {
            "Methane": (190.6, 46.0, 0.011),
            "Ethane": (305.3, 48.7, 0.099),
            "Propane": (369.8, 42.5, 0.152),
            "n-Butane": (425.1, 37.9, 0.200),
            "CO2": (304.1, 73.8, 0.225),
            "N2": (126.2, 34.0, 0.037),
            "Water": (647.1, 220.6, 0.344),
        }

        selected_common = st.selectbox(
            "Select from database",
            [""] + list(common_components.keys()),
            key="common_comp_select",
        )

        if selected_common and st.button("Add from Database", key="add_from_db"):
            tc_db, pc_db, w_db = common_components[selected_common]
            new_comp = ComponentData(name=selected_common, tc=tc_db, pc=pc_db, w=w_db)
            config.add_component(new_comp)
            st.success(f"Added {selected_common} from database")
            st.rerun()

        st.info(
            "Note: Database components only include Tc, Pc, and ω. For models requiring additional parameters (RKPR, PSRK), you'll need to add them manually or use bulk import."
        )

    # Bulk import from Excel
    with st.expander("📋 Bulk Import from Excel"):
        st.markdown(ModelClass.get_bulk_import_format())
        paste_area = st.text_area(
            "Paste your data here:",
            height=150,
            placeholder="",
            help="Paste data from Excel (tab-separated values)",
        )

        col1, col2 = st.columns([1, 3])

        with col1:
            has_header = st.checkbox("First row is header", value=True)

        with col2:
            delimiter_option = st.radio(
                "Delimiter",
                ["Whitespace (Tab/Space)", "Comma"],
                horizontal=True,
                help="Choose the delimiter used in your data",
            )

            delimiter_map = {
                "Whitespace (Tab/Space)": None,  # None uses split() which handles any whitespace
                "Comma": ",",
            }
            delimiter = delimiter_map[delimiter_option]

        if st.button("📥 Import Components", type="primary"):
            if paste_area.strip():
                try:
                    # Parse pasted data
                    lines = paste_area.strip().split("\n")

                    # Skip header if present
                    start_idx = 1 if has_header else 0

                    imported_count = 0
                    errors = []

                    for i, line in enumerate(lines[start_idx:], start=start_idx + 1):
                        if not line.strip():
                            continue

                        try:
                            # Split by delimiter
                            parts = [p.strip() for p in line.split(delimiter)]
                            component, error = ModelClass.parse_bulk_import_line(
                                parts, i
                            )

                            # Add component
                            config.add_component(component)
                            imported_count += 1

                        except ValueError as e:
                            errors.append(
                                f"Line {i}: Could not convert values to numbers - {str(e)}"
                            )
                        except Exception as e:
                            errors.append(f"Line {i}: {str(e)}")

                    # Show results
                    if imported_count > 0:
                        st.success(
                            f"✅ Successfully imported {imported_count} component(s)!"
                        )
                        st.rerun()

                    if errors:
                        st.warning("⚠️ Some lines had errors:")
                        for error in errors:
                            st.text(error)

                    if imported_count == 0 and not errors:
                        st.error("No valid data found. Please check your format.")

                except Exception as e:
                    st.error(f"Error parsing data: {str(e)}")
            else:
                st.warning("Please paste some data first!")

        # Show example data button
        if st.button("📝 Show Example Data"):
            example_data = ModelClass.get_bulk_import_example()
            st.code(example_data, language=None)
            st.info(
                "Copy this example data and paste it in the text area above to test the import feature!"
            )

    st.markdown("---")

    # Mixing Rule Configuration
    st.header("3. Configure Mixing Rule")

    n_components = len(config.components)

    # Get the selected model class
    ModelClass = CUBIC_EOS_REGISTRY[config.model_type]

    # Check if model requires mixing rule
    if not ModelClass.requires_mixing_rule():
        st.info(
            f"ℹ️ {ModelClass.get_display_name()} uses built-in mixing rules. No additional configuration needed."
        )
        config.set_mixing_rule(None)
        st.markdown("---")
    elif n_components < 2:
        st.warning("⚠️ Add at least 2 components to configure mixing rules")
    else:
        # Build mixing rule options from registry
        mixing_rule_options = {
            key: cls.get_display_name() for key, cls in MIXING_RULE_REGISTRY.items()
        }

        mixing_rule_type = st.selectbox(
            "Mixing Rule Type",
            list(mixing_rule_options.keys()),
            format_func=lambda x: mixing_rule_options[x],
            help="Select the mixing rule for the equation of state",
        )

        # Get the selected mixing rule class from registry
        MixingRuleClass = MIXING_RULE_REGISTRY[mixing_rule_type]

        # Call the class's setup_ui method to configure and instantiate
        component_names = [comp.name for comp in config.components]
        mixrule_instance = MixingRuleClass.setup_ui(
            n_components=n_components,
            component_names=component_names,
            key_prefix=mixing_rule_type.lower(),
        )

        # Set the configured mixing rule
        config.set_mixing_rule(mixrule_instance)

    st.markdown("---")

    # Model Summary and Creation
    st.header("4. Model Summary")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.json(config.to_dict(), expanded=False)

    with col2:
        if st.button("✅ Create Model", type="primary", disabled=(n_components < 2)):
            st.session_state.model = ModelClass.get_eos_object(config=config)
            st.session_state.model_created = True
            st.success("Model created successfully!")
            st.balloons()

        if n_components < 2:
            st.error("Add at least 2 components to create a model")

        if st.session_state.model_created:
            st.success("✓ Model is ready for calculations")


def show_phase_envelope():
    """Phase envelope calculation page"""
    st.title("Phase Envelope Calculations")
    st.markdown("Calculate and visualize phase envelopes for multicomponent mixtures")
    st.markdown("---")

    if not st.session_state.model_created:
        st.warning(
            "⚠️ Please configure and create a model first in the 'Model Configuration' page"
        )
        return
    else:
        model = st.session_state.model

    config = st.session_state.model_config
    n_components = len(config.components)

    st.header("Mixture Composition")

    # Composition input
    st.write("Enter mole fractions (must sum to 1.0):")

    col1, col2 = st.columns(2)
    with col1:
        cols = st.columns(min(n_components, 4))
        z = []

        for i, comp in enumerate(config.components):
            with cols[i % 4]:
                z_i = st.number_input(
                    f"{comp.name}",
                    value=1.0 / n_components,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                    format="%.3f",
                    key=f"z_{i}",
                )
                z.append(z_i)

        z = np.array(z)
        z_sum = np.sum(z)

        z = z / z_sum

    with col2:
        st.write("**Normalized Mole Fractions:**")
        for i, comp in enumerate(config.components):
            st.text(f"{comp.name}: {z[i]:.4f}")

    st.markdown("---")

    # Calculation options
    st.header("Calculation Options")

    col1, col2 = st.columns(2)

    with col1:
        start_temp = st.number_input(
            "Starting Temperature [K]", value=150.0, min_value=0.0, step=10.0
        )

    with col2:
        if st.button("🔬 Calculate Phase Envelope", type="primary"):
            with st.spinner("Calculating phase envelope..."):
                dew = model.phase_envelope_pt(z, kind="dew", t0=start_temp, p0=0.1)
                st.session_state.envelope_results = {"dew": dew}
                print(dew)

                st.success("✅ Calculation completed!")

    # Display results
    if "envelope_results" in st.session_state:
        st.markdown("---")
        st.header("Results")

        results = st.session_state.envelope_results

        dew = results["dew"]

        # Create plot
        fig = go.Figure()

        # Add dew point curve
        fig.add_trace(
            go.Scatter(
                x=dew["T"],
                y=dew["P"],
                mode="lines",
                name="Dew Point",
                line=dict(color="blue", width=2),
            )
        )

        # # Add bubble point curve
        # fig.add_trace(
        #     go.Scatter(
        #         x=results["T"],
        #         y=results["P_bubble"],
        #         mode="lines",
        #         name="Bubble Point",
        #         line=dict(color="red", width=2),
        #     )
        # )

        # # Add critical point
        # fig.add_trace(
        #     go.Scatter(
        #         x=[results["T_critical"]],
        #         y=[results["P_critical"]],
        #         mode="markers",
        #         name="Critical Point",
        #         marker=dict(size=12, color="green", symbol="star"),
        #     )
        # )

        # # Add two-phase region
        # fig.add_trace(
        #     go.Scatter(
        #         x=list(results["T"]) + list(results["T"][::-1]),
        #         y=list(results["P_dew"]) + list(results["P_bubble"][::-1]),
        #         fill="toself",
        #         fillcolor="rgba(128, 128, 128, 0.2)",
        #         line=dict(width=0),
        #         name="Two-Phase Region",
        #         showlegend=True,
        #     )
        # )

        # fig.update_layout(
        #     title="Phase Envelope Diagram",
        #     xaxis_title="Temperature [K]",
        #     yaxis_title="Pressure [bar]",
        #     hovermode="closest",
        #     template="plotly_white",
        #     height=600,
        #     legend=dict(x=0.02, y=0.98),
        # )

        st.plotly_chart(fig, use_container_width=True)

        # # Display critical point info
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.metric("Critical Temperature", f"{results['T_critical']:.2f} K")
        # with col2:
        #     st.metric("Critical Pressure", f"{results['P_critical']:.2f} bar")
        # with col3:
        #     st.metric("Points Calculated", len(results["T"]))

        # # Export data
        # with st.expander("📥 Export Data"):
        #     export_data = {
        #         "Temperature_K": results["T"].tolist(),
        #         "Pressure_Dew_bar": results["P_dew"].tolist(),
        #         "Pressure_Bubble_bar": results["P_bubble"].tolist(),
        #         "Composition": results["composition"].tolist(),
        #     }

        #     st.download_button(
        #         label="Download JSON",
        #         data=json.dumps(export_data, indent=2),
        #         file_name="phase_envelope.json",
        #         mime="application/json",
        #     )


def show_gpec_diagram():
    """GPEC (Global Phase Equilibrium Calculations) diagram page"""
    st.title("GPEC Diagrams")
    st.markdown("Global Phase Equilibrium Calculations for binary systems")
    st.markdown("---")

    if not st.session_state.model_created:
        st.warning(
            "⚠️ Please configure and create a model first in the 'Model Configuration' page"
        )
        return

    config = st.session_state.model_config
    n_components = len(config.components)

    if n_components != 2:
        st.error(
            "❌ GPEC diagrams are only available for binary systems (2 components)"
        )
        st.info(
            f"Current system has {n_components} components. Please reconfigure with exactly 2 components."
        )
        return

    st.success(
        f"✓ Binary system: {config.components[0].name} - {config.components[1].name}"
    )

    model = st.session_state.model
    gpec = yaeos.GPEC(model, max_pressure=300)

    st.markdown("---")

    # Diagram type selection
    diagram_type = st.radio(
        "Select Diagram Type",
        [
            "Pxy (Pressure-Composition)",
            "Txy (Temperature-Composition)",
            "PT Projection",
        ],
        horizontal=True,
    )

    st.header("Global Phase Diagram")
    fig = go.Figure()
    for i, pure in enumerate(gpec._pures):
        fig.add_trace(
            go.Scatter(
                x=pure["T"],
                y=pure["P"],
                mode="lines",
                name=f"Pure {config.components[i].name}",
                line=dict(width=2, dash="dot"),
            )
        )
    fig.add_trace(
        go.Scatter(
            x=gpec._cl21["T"],
            y=gpec._cl21["P"],
            mode="lines",
            name="Critical Locus 2->1",
            line=dict(color="black", width=2),
        )
    )

    if gpec._cl12 is not None:
        fig.add_trace(
            go.Scatter(
                x=gpec._cl12["T"],
                y=gpec._cl12["P"],
                mode="lines",
                name="Critical Locus 1->2",
                line=dict(color="gray", width=2),
            )
        )
    if gpec._cl_ll is not None:
        fig.add_trace(
            go.Scatter(
                x=gpec._cl_ll["T"],
                y=gpec._cl_ll["P"],
                mode="lines",
                name="Critical Locus LL",
                line=dict(color="black", width=2),
            )
        )
        if gpec._llv_ll is not None:
            fig.add_trace(
                go.Scatter(
                    x=gpec._llv_ll["T"],
                    y=gpec._llv_ll["P"],
                    mode="lines",
                    name="Vapor-Liquid-Liquid",
                    line=dict(color="purple", width=2, dash="dash"),
                )
            )

    st.plotly_chart(fig, use_container_width=False)
    st.markdown("---")

    if diagram_type == "Pxy (Pressure-Composition)":
        st.header("Pxy Diagram at Constant Temperature")

        col1, col2 = st.columns(2)

        with col1:
            n_temps = st.slider("Number of Isotherms", 1, 5, 3)
            T_min = st.number_input("Min Temperature [K]", value=250.0, step=10.0)
            T_max = st.number_input("Max Temperature [K]", value=350.0, step=10.0)

        with col2:
            n_points = st.slider("Points per Isotherm", 20, 100, 50)

        if st.button("🔬 Calculate Pxy Diagram", type="primary"):
            with st.spinner("Calculating Pxy diagram..."):
                temperatures = np.linspace(T_min, T_max, n_temps)

                fig = go.Figure()

                for T in temperatures:
                    pxys = gpec.calc_pxy(T)
                    print(pxys)
                    color = px.colors.sample_colorscale(
                        "viridis", (T - T_min) / (T_max - T_min)
                    )[0]

                    for pxy in pxys:
                        if pxy:
                            x = pxy["x"][:, 0, 0]
                            y = pxy["w"][:, 0]
                            P = pxy["P"][:]

                            fig.add_trace(
                                go.Scatter(
                                    x=x,
                                    y=P,
                                    mode="lines",
                                    name=f"{T:.1f}K",
                                    line=dict(width=2, color=color),
                                )
                            )
                            fig.add_trace(
                                go.Scatter(
                                    x=y,
                                    y=P,
                                    mode="lines",
                                    name=f"{T:.1f}K",
                                    line=dict(width=2, color=color),
                                    showlegend=False,
                                )
                            )

                fig.update_layout(
                    title="Pxy Diagram (Pressure-Composition)",
                    xaxis_title=f"Mole Fraction {config.components[0].name}",
                    yaxis_title="Pressure [bar]",
                    hovermode="closest",
                    template="plotly_white",
                    height=600,
                )

                st.plotly_chart(fig, use_container_width=True)

    elif diagram_type == "Txy (Temperature-Composition)":
        st.header("Txy Diagram at Constant Pressure")

        col1, col2 = st.columns(2)

        with col1:
            n_pressures = st.slider("Number of Isobars", 1, 5, 3)
            P_min = st.number_input("Min Pressure [bar]", value=1.0, step=1.0)
            P_max = st.number_input("Max Pressure [bar]", value=10.0, step=1.0)

        with col2:
            n_points = st.slider("Points per Isobar", 20, 100, 50)

        if st.button("🔬 Calculate Txy Diagram", type="primary"):
            with st.spinner("Calculating Txy diagram..."):
                pressures = np.linspace(P_min, P_max, n_pressures)

                fig = go.Figure()

                for i, P in enumerate(pressures):
                    txys = gpec.calc_txy(P)
                    color = px.colors.sample_colorscale("viridis", P / P_max)[0]

                    for txy in txys:
                        if txy:
                            x = txy["x"][:, 0, 0]
                            y = txy["w"][:, 0]
                            T = txy["T"][:]

                            fig.add_trace(
                                go.Scatter(
                                    x=x,
                                    y=T,
                                    mode="lines",
                                    name=f"{P:.1f}bar",
                                    line=dict(width=2, color=color),
                                )
                            )
                            fig.add_trace(
                                go.Scatter(
                                    x=y,
                                    y=T,
                                    mode="lines",
                                    name=f"{P:.1f}bar",
                                    line=dict(width=2, color=color),
                                    showlegend=False,
                                )
                            )
                fig.update_layout(
                    title="Txy Diagram (Temperature-Composition)",
                    xaxis_title=f"Mole Fraction {config.components[0].name}",
                    yaxis_title="Temperature [K]",
                    hovermode="closest",
                    template="plotly_white",
                    height=600,
                )

                st.plotly_chart(fig, use_container_width=True)

    else:  # PT Projection
        st.header("PT Projection - Critical Locus")

        st.info(
            """
        The PT projection shows the phase behavior of the binary system over a range 
        of temperatures and pressures, including the critical locus.
        """
        )

        col1, col2 = st.columns(2)

        with col1:
            n_compositions = st.slider("Number of Compositions", 5, 20, 11)

        with col2:
            n_points = st.slider("Points per Composition", 20, 100, 50)

        if st.button("🔬 Calculate PT Projection", type="primary"):
            with st.spinner("Calculating PT projection and critical locus..."):
                compositions = np.linspace(0, 1, n_compositions)

                fig = go.Figure()

                T_critical_list = []
                P_critical_list = []

                for i, x1 in enumerate(compositions):
                    # Mock phase envelope for this composition
                    T = np.linspace(200, 400, n_points)
                    P = 20 + 30 * np.exp(-((T - 300) ** 2) / 5000) * (
                        1 + 0.5 * x1 * (1 - x1)
                    )
                    P += np.random.normal(0, 0.5, n_points)

                    # Find approximate critical point
                    critical_idx = np.argmax(P)
                    T_critical_list.append(T[critical_idx])
                    P_critical_list.append(P[critical_idx])

                    # Plot envelope
                    fig.add_trace(
                        go.Scatter(
                            x=T,
                            y=P,
                            mode="lines",
                            name=f"x₁={x1:.2f}",
                            line=dict(width=1),
                            opacity=0.6,
                        )
                    )

                # Add critical locus
                fig.add_trace(
                    go.Scatter(
                        x=T_critical_list,
                        y=P_critical_list,
                        mode="lines+markers",
                        name="Critical Locus",
                        line=dict(color="black", width=3),
                        marker=dict(size=8, color="red", symbol="star"),
                    )
                )

                fig.update_layout(
                    title="PT Projection with Critical Locus",
                    xaxis_title="Temperature [K]",
                    yaxis_title="Pressure [bar]",
                    hovermode="closest",
                    template="plotly_white",
                    height=600,
                    showlegend=True,
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display critical locus data
                with st.expander("📊 Critical Locus Data"):
                    import pandas as pd

                    df_critical = pd.DataFrame(
                        {
                            f"x₁ ({config.components[0].name})": compositions,
                            "T_critical [K]": T_critical_list,
                            "P_critical [bar]": P_critical_list,
                        }
                    )

                    st.dataframe(df_critical, use_container_width=True)


if __name__ == "__main__":
    main()
