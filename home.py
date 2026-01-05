import streamlit as st


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
        
        - Configure thermodynamic models (ArModel & GeModel)
        - Perform phase equilibrium calculations
        - Generate phase envelopes and GPEC diagrams
        - Analyze binary and multicomponent systems
        """
        )

        st.header("Available Model Types")
        
        st.subheader("🔷 ArModel (Residual Helmholtz)")
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
        - Temperature-dependent variants
        """
        )
        
        st.subheader("🔶 GeModel (Excess Gibbs)")
        st.markdown(
            """
        **Activity Coefficient Models:**
        - NRTL (Non-Random Two-Liquid)
        - UNIQUAC (Universal Quasi-Chemical)
        - UNIFAC variants (VLE, PSRK, Dortmund)
        """
        )

    with col2:
        st.header("Quick Start")
        st.info(
            """
        **Step 1:** Choose model category (ArModel or GeModel)
        
        **Step 2:** Select specific model and add components
        
        **Step 3:** Configure parameters (mixing rules for ArModel)
        
        **Step 4:** Run calculations (availability depends on model type)
        """
        )

        st.warning(
            """
        ⚠️ **Important:** 
        - Phase Envelopes & GPEC require ArModel
        - Some calculations are GeModel-specific
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
        
        **Requires:** ArModel (Residual Helmholtz)
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
        
        **Requires:** ArModel (Residual Helmholtz)
        """
        )


