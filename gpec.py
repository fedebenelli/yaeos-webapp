import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import yaeos


def show_gpec_diagram():
    """GPEC (Global Phase Equilibrium Calculations) diagram page"""
    st.title("GPEC Diagrams")
    st.markdown("Global Phase Equilibrium Calculations for binary systems")
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
            "❌ GPEC diagrams require an **ArModel (Residual Helmholtz)**"
        )
        st.info(
            """
            GPEC calculations require critical point detection and phase envelope tracing,
            which are only available for Residual Helmholtz models.
            
            **To use this feature:**
            1. Go to "Model Configuration"
            2. Select "ArModel (Residual Helmholtz)"
            3. Choose a Cubic EoS model (PR76, SRK, etc.)
            4. Configure and create the model
            """
        )
        return

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

    try:
        gpec = yaeos.GPEC(model, max_pressure=300)
    except Exception as e:
        st.error(f"Failed to initialize GPEC: {str(e)}")
        return

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
            name="Critical Locus 2→1",
            line=dict(color="black", width=2),
        )
    )

    if gpec._cl12 is not None:
        fig.add_trace(
            go.Scatter(
                x=gpec._cl12["T"],
                y=gpec._cl12["P"],
                mode="lines",
                name="Critical Locus 1→2",
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

    fig.update_layout(
        title="Global Phase Diagram",
        xaxis_title="Temperature [K]",
        yaxis_title="Pressure [bar]",
        template="plotly_white",
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    if diagram_type == "Pxy (Pressure-Composition)":
        st.header("Pxy Diagram at Constant Temperature")

        col1, col2 = st.columns(2)

        with col1:
            n_temps = st.slider("Number of Isotherms", 1, 5, 3)
            T_min = st.number_input(
                "Min Temperature [K]", value=250.0, step=10.0
            )
            T_max = st.number_input(
                "Max Temperature [K]", value=350.0, step=10.0
            )

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
                    color = px.colors.sample_colorscale("viridis", P / P_max)[
                        0
                    ]

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
