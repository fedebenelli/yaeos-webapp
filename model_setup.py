import streamlit as st
from models import ModelType
from models.excess_gibbs import GE_MODEL_REGISTRY
from models.residual_helmholtz.cubic.mixing_rules import MIXING_RULE_REGISTRY
from models.residual_helmholtz import CUBIC_EOS_REGISTRY
from thermo_utils import ComponentData


def show_model_configuration():
    """Model configuration page"""
    st.title("Model Configuration")
    st.markdown(
        "Configure your thermodynamic model, components, and parameters"
    )
    st.markdown("---")

    config = st.session_state.model_config

    # =========================================================================
    # STEP 1: Model Category Selection (ArModel vs GeModel)
    # =========================================================================
    st.header("1. Select Model Category")

    model_category = st.radio(
        "Model Category",
        [ModelType.RESIDUAL_HELMHOLTZ, ModelType.EXCESS_GIBBS],
        help="ArModel (Residual Helmholtz) for EoS calculations, GeModel (Excess Gibbs) for activity coefficients",
    )

    # Update config if category changed
    if config.model_category != model_category:
        config.model_category = model_category
        config.mixing_rule = (
            None  # Reset mixing rule when switching categories
        )
        st.session_state.model_created = False  # Invalidate existing model

    st.markdown("---")

    # =========================================================================
    # STEP 2: Specific Model Selection
    # =========================================================================
    st.header("2. Select Specific Model")

    if config.is_ar_model():
        # ArModel (Cubic EoS) Selection
        model_options = {
            key: cls.get_display_name()
            for key, cls in CUBIC_EOS_REGISTRY.items()
        }

        config.model_type = st.selectbox(
            "Cubic EoS Model",
            list(model_options.keys()),
            format_func=lambda x: model_options[x],
            help="Select the cubic equation of state model",
        )

        ModelClass = CUBIC_EOS_REGISTRY[config.model_type]

    else:  # GeModel
        # GeModel Selection
        model_options = {
            key: cls.get_display_name()
            for key, cls in GE_MODEL_REGISTRY.items()
        }

        config.model_type = st.selectbox(
            "Excess Gibbs Model",
            list(model_options.keys()),
            format_func=lambda x: model_options[x],
            help="Select the excess Gibbs energy model",
        )

        ModelClass = GE_MODEL_REGISTRY[config.model_type]

    # Display model description
    st.info(f"ℹ️ {ModelClass.get_description()}")

    # Show required parameters info (for ArModel)
    if config.is_ar_model():
        required_params = ModelClass.get_required_parameters()
        if required_params:
            param_names = ", ".join(required_params)
            st.warning(
                f"⚠️ This model requires additional parameters: {param_names}"
            )

    st.markdown("---")

    # =========================================================================
    # STEP 3: Component Configuration
    # =========================================================================
    st.header("3. Add Components")

    col1, col2 = st.columns([3, 1], gap="small")

    with col1:
        st.subheader("Current Components")
        if config.components:
            for i, comp in enumerate(config.components):
                comp_info = f"{i+1}. {comp.name}: Tc={comp.tc}K, Pc={comp.pc}bar, ω={comp.w}"

                # Add model-specific parameters if present
                if comp.zc is not None:
                    comp_info += f", Zc={comp.zc}"
                if (
                    comp.c1 is not None
                    or comp.c2 is not None
                    or comp.c3 is not None
                ):
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

    # Component input depends on model type
    if config.is_ar_model():
        # For ArModel, use the model's component setup UI
        new_comp = ModelClass.setup_component_ui(key_prefix="add_comp")
    else:
        # For GeModel, only basic properties needed (some models may need groups)
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

        if selected_common and st.button(
            "Add from Database", key="add_from_db"
        ):
            tc_db, pc_db, w_db = common_components[selected_common]
            new_comp = ComponentData(
                name=selected_common, tc=tc_db, pc=pc_db, w=w_db
            )
            config.add_component(new_comp)
            st.success(f"Added {selected_common} from database")
            st.rerun()

        if config.is_ar_model():
            st.info(
                "Note: Database components only include Tc, Pc, and ω. For models requiring additional parameters (RKPR, PSRK), you'll need to add them manually or use bulk import."
            )

    # Bulk import (only for ArModel with component-specific requirements)
    if config.is_ar_model():
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
                    "Whitespace (Tab/Space)": None,
                    "Comma": ",",
                }
                delimiter = delimiter_map[delimiter_option]

            if st.button("📥 Import Components", type="primary"):
                if paste_area.strip():
                    try:
                        lines = paste_area.strip().split("\n")
                        start_idx = 1 if has_header else 0

                        imported_count = 0
                        errors = []

                        for i, line in enumerate(
                            lines[start_idx:], start=start_idx + 1
                        ):
                            if not line.strip():
                                continue

                            try:
                                parts = [
                                    p.strip() for p in line.split(delimiter)
                                ]
                                component, error = (
                                    ModelClass.parse_bulk_import_line(parts, i)
                                )

                                if error:
                                    errors.append(error)
                                else:
                                    config.add_component(component)
                                    imported_count += 1

                            except Exception as e:
                                errors.append(f"Line {i}: {str(e)}")

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
                            st.error(
                                "No valid data found. Please check your format."
                            )

                    except Exception as e:
                        st.error(f"Error parsing data: {str(e)}")
                else:
                    st.warning("Please paste some data first!")

            if st.button("📄 Show Example Data"):
                example_data = ModelClass.get_bulk_import_example()
                st.code(example_data, language=None)

    st.markdown("---")

    # =========================================================================
    # STEP 4: Model-Specific Configuration
    # =========================================================================
    n_components = len(config.components)

    if config.is_ar_model():
        # ArModel: Mixing Rule Configuration
        st.header("4. Configure Mixing Rule")

        if not ModelClass.requires_mixing_rule():
            st.info(
                f"ℹ️ {ModelClass.get_display_name()} uses built-in mixing rules. No additional configuration needed."
            )
            config.set_mixing_rule(None)
        elif n_components < 2:
            st.warning("⚠️ Add at least 2 components to configure mixing rules")
        else:
            mixing_rule_options = {
                key: cls.get_display_name()
                for key, cls in MIXING_RULE_REGISTRY.items()
            }

            mixing_rule_type = st.selectbox(
                "Mixing Rule Type",
                list(mixing_rule_options.keys()),
                format_func=lambda x: mixing_rule_options[x],
                help="Select the mixing rule for the equation of state",
            )

            MixingRuleClass = MIXING_RULE_REGISTRY[mixing_rule_type]

            component_names = [comp.name for comp in config.components]
            mixrule_instance = MixingRuleClass.setup_ui(
                n_components=n_components,
                component_names=component_names,
                key_prefix=mixing_rule_type.lower(),
            )

            config.set_mixing_rule(mixrule_instance)

    else:  # GeModel
        # GeModel: Direct Parameter Configuration
        st.header("4. Configure Model Parameters")

        if n_components < 2:
            st.warning("⚠️ Add at least 2 components to configure parameters")
        else:
            component_names = [comp.name for comp in config.components]

            # The GeModel setup_ui returns a configured instance
            st.session_state.ge_model_instance = ModelClass.setup_ui(
                n_components=n_components,
                component_names=component_names,
                key_prefix=config.model_type.lower(),
            )

    st.markdown("---")

    # =========================================================================
    # STEP 5: Model Summary and Creation
    # =========================================================================
    st.header("5. Model Summary")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.json(config.to_dict(), expanded=False)

    with col2:
        can_create = n_components >= 2

        if st.button(
            "✅ Create Model", type="primary", disabled=(not can_create)
        ):
            try:
                if config.is_ar_model():
                    # Create ArModel
                    st.session_state.model = ModelClass.get_eos_object(
                        config=config
                    )
                else:
                    # Create GeModel
                    st.session_state.model = (
                        st.session_state.ge_model_instance.get_ge_object()
                    )

                st.session_state.model_created = True
                st.session_state.model_category = config.model_category
                st.success("Model created successfully!")
                st.balloons()

            except Exception as e:
                st.error(f"Error creating model: {str(e)}")

        if not can_create:
            st.error("Add at least 2 components to create a model")

        if st.session_state.model_created:
            category = "ArModel" if config.is_ar_model() else "GeModel"
            st.success(f"✓ {category} is ready for calculations")
