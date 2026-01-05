import streamlit as st
import numpy as np
import plotly.graph_objects as go


def show_phase_envelope():
    """Phase envelope calculation page"""
    st.title("Phase Envelope Calculations")
    st.markdown(
        "Calculate and visualize phase envelopes for multicomponent mixtures"
    )
    st.markdown("---")

    # =========================================================================
    # ArModel Validation
    # =========================================================================
    if not st.session_state.model_created:
        st.warning(
            "⚠️ Please configure and create a model first in the 'Model Configuration' page"
        )
        return
    
    config = st.session_state.model_config
    
    if not config.is_ar_model():
        st.error(
            "❌ Phase envelope calculations require an **ArModel (Residual Helmholtz)**"
        )
        st.info(
            """
            Phase envelopes use thermodynamic derivatives from the Residual Helmholtz energy, 
            which are not available in Excess Gibbs models.
            
            **To use this feature:**
            1. Go to "Model Configuration"
            2. Select "ArModel (Residual Helmholtz)"
            3. Choose a Cubic EoS model (PR76, SRK, etc.)
            4. Configure and create the model
            """
        )
        return

    model = st.session_state.model
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
                try:
                    dew = model.phase_envelope_pt(
                        z, kind="dew", t0=start_temp, p0=0.1
                    )
                    st.session_state.envelope_results = {"dew": dew}

                    st.success("✅ Calculation completed!")
                except Exception as e:
                    st.error(f"Calculation failed: {str(e)}")

    # Display results
    if "envelope_results" in st.session_state:
        st.markdown("---")
        st.header("Results")

        results = st.session_state.envelope_results
        dew = results["dew"]

        # Create plot
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dew["T"],
                y=dew["P"],
                mode="lines",
                name="Dew Point",
                line=dict(color="blue", width=2),
            )
        )

        fig.update_layout(
            title="Phase Envelope Diagram",
            xaxis_title="Temperature [K]",
            yaxis_title="Pressure [bar]",
            hovermode="closest",
            template="plotly_white",
            height=600,
        )

        st.plotly_chart(fig, use_container_width=True)
