"""Flash calculations page for GeModel (Excess Gibbs) models.

This module provides the Streamlit UI for performing two-phase flash
calculations using GeModel objects from yaeos.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any


def flash_ge_single(model, z: np.ndarray, temperature: float, k0=None):
    """Perform single flash calculation with error handling."""
    try:
        result = model.flash_t(z=z, temperature=temperature, k0=k0)
        result["converged"] = True

        # Validate results
        if result["beta"] < 0 or result["beta"] > 1:
            result["converged"] = False

        return result
    except Exception as e:
        return {
            "x": z.copy(),
            "y": z.copy(),
            "T": temperature,
            "beta": 0.0,
            "converged": False,
            "error": str(e),
        }


def show_flash_ge_page():
    """Flash calculations page for GeModel."""
    st.title("Flash Calculations - GeModel")
    st.markdown("Two-phase equilibrium calculations using Excess Gibbs models")
    st.markdown("---")

    # =========================================================================
    # GeModel Validation
    # =========================================================================
    if not st.session_state.model_created:
        st.warning(
            "⚠️ Please configure and create a model first in the 'Model Configuration' page"
        )
        return

    config = st.session_state.model_config

    if not config.is_ge_model():
        st.error(
            "❌ Flash calculations on this page require a **GeModel (Excess Gibbs)**"
        )
        st.info(
            """
            This page performs isothermal flash calculations, which are specific 
            to Excess Gibbs energy models.
            
            **To use this feature:**
            1. Go to "Model Configuration"
            2. Select "GeModel (Excess Gibbs)"
            3. Choose a model (NRTL, UNIFAC, etc.)
            4. Configure and create the model
            """
        )
        return

    model = st.session_state.model
    n_components = len(config.components)
    component_names = [comp.name for comp in config.components]

    # =========================================================================
    # Calculation Mode Selection
    # =========================================================================
    st.header("Calculation Mode")

    calc_mode = st.radio(
        "Select calculation type",
        ["Single Point", "Grid Calculation", "Isothermal Path"],
        horizontal=True,
    )

    st.markdown("---")

    # =========================================================================
    # SINGLE POINT MODE
    # =========================================================================
    if calc_mode == "Single Point":
        st.header("Single Point Flash Calculation")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Composition")
            st.write("Enter mole fractions (will be normalized):")

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
                        format="%.4f",
                        key=f"single_z_{i}",
                    )
                    z.append(z_i)

            z = np.array(z)
            z = z / np.sum(z)  # Normalize

            st.write("**Normalized composition:**")
            for i, comp in enumerate(config.components):
                st.text(f"{comp.name}: {z[i]:.4f}")

        with col2:
            st.subheader("Conditions")
            temperature = st.number_input(
                "Temperature [K]",
                value=298.15,
                min_value=100.0,
                max_value=1000.0,
                step=1.0,
                format="%.2f",
            )

            if st.button(
                "🔬 Calculate Flash", type="primary", key="calc_single"
            ):
                with st.spinner("Calculating..."):
                    result = flash_ge_single(model, z, temperature)
                    st.session_state.flash_result = result

        # Display results
        if "flash_result" in st.session_state:
            st.markdown("---")
            st.header("Results")

            result = st.session_state.flash_result

            if result["converged"]:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Temperature", f"{result['T']:.2f} K")
                with col2:
                    st.metric("Phase-y Fraction (β)", f"{result['beta']:.4f}")
                with col3:
                    status = (
                        "Two-phase"
                        if 0 < result["beta"] < 1
                        else "Single-phase"
                    )
                    st.metric("Status", status)

                # Phase compositions
                st.subheader("Phase Compositions")

                comp_data = {
                    "Component": component_names,
                    "Feed (z)": z,
                    "Phase-(x)": result["x"],
                    "Phase-(y)": result["y"],
                    "K-value (y/x)": result["y"] / result["x"],
                }

                df = pd.DataFrame(comp_data)
                st.dataframe(
                    df.style.format(
                        {
                            "Feed (z)": "{:.4f}",
                            "Phase-(x)": "{:.4f}",
                            "Phase-(y)": "{:.4f}",
                            "K-value (y/x)": "{:.4f}",
                        }
                    ),
                    use_container_width=True,
                )

                # Visualization
                fig = go.Figure()

                x_pos = np.arange(n_components)
                width = 0.25

                fig.add_trace(
                    go.Bar(x=x_pos - width, y=z, name="Feed (z)", width=width)
                )
                fig.add_trace(
                    go.Bar(
                        x=x_pos, y=result["x"], name="Phase-(x)", width=width
                    )
                )
                fig.add_trace(
                    go.Bar(
                        x=x_pos + width,
                        y=result["y"],
                        name="Phase-(y)",
                        width=width,
                    )
                )

                fig.update_layout(
                    title="Phase Compositions",
                    xaxis=dict(
                        tickmode="array",
                        tickvals=x_pos,
                        ticktext=component_names,
                    ),
                    yaxis_title="Mole Fraction",
                    barmode="group",
                    template="plotly_white",
                    height=400,
                )

                st.plotly_chart(fig, use_container_width=True)

            else:
                st.error("❌ Flash calculation did not converge")
                if "error" in result:
                    st.error(f"Error: {result['error']}")

    # =========================================================================
    # GRID CALCULATION MODE
    # =========================================================================
    elif calc_mode == "Grid Calculation":
        st.header("Grid Flash Calculation")
        st.info("Calculate flash over multiple compositions and temperatures")

        # Temperature range
        st.subheader("Temperature Range")
        col1, col2, col3 = st.columns(3)

        with col1:
            T_min = st.number_input(
                "Min Temperature [K]", value=298.15, step=10.0
            )
        with col2:
            T_max = st.number_input(
                "Max Temperature [K]", value=348.15, step=10.0
            )
        with col3:
            n_temps = st.slider("Number of temperatures", 2, 20, 5)

        temperatures = np.linspace(T_min, T_max, n_temps)

        # Composition grid
        st.subheader("Composition Grid")

        if n_components == 2:
            st.write("For binary systems, vary the first component:")
            n_comps = st.slider("Number of compositions", 3, 20, 10)

            x1_range = np.linspace(0.0, 1.0, n_comps)
            z_points = [np.array([x1, 1 - x1]) for x1 in x1_range]

        else:
            st.warning(
                "Grid mode for 3+ components: varying first component only"
            )
            n_comps = st.slider("Number of compositions", 3, 15, 8)

            # Fix ratios for components 2+
            z_base = np.ones(n_components)
            z_base = z_base / np.sum(z_base)

            z_points = []
            low_limit = 1e-5
            upper_limit = 1 - low_limit
            for alpha in np.linspace(low_limit, upper_limit, n_comps):
                z = z_base.copy()
                z[0] = alpha
                remaining = (1 - alpha) / (n_components - 1)
                z[1:] = remaining
                z_points.append(z)

        st.write(
            f"**Total calculations:** {len(z_points) * len(temperatures)}"
        )

        if st.button("🔬 Calculate Grid", type="primary", key="calc_grid"):
            with st.spinner(
                f"Calculating {len(z_points) * len(temperatures)} flash points..."
            ):
                results = []

                progress_bar = st.progress(0)
                total = len(z_points) * len(temperatures)
                count = 0

                for z in z_points:
                    k0 = model.stability_analysis(z, temperatures[0])[0]["w"]/z
                    for T in temperatures:
                        result = flash_ge_single(model, z, T, k0=k0)

                        row = {"T": T}
                        for i in range(n_components):
                            row[f"z_{i+1}"] = z[i]
                            row[f"x_{i+1}"] = result["x"][i]
                            row[f"y_{i+1}"] = result["y"][i]

                        row["beta"] = result["beta"]
                        row["converged"] = result["converged"]

                        k0 = result["y"] / result["x"]

                        results.append(row)

                        count += 1
                        progress_bar.progress(count / total)

                st.session_state.grid_results = pd.DataFrame(results)
                progress_bar.empty()
                st.success("✅ Grid calculation complete!")

        # Display grid results
        if "grid_results" in st.session_state:
            st.markdown("---")
            st.header("Grid Results")

            df = st.session_state.grid_results

            # Summary statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Points", len(df))
            with col2:
                converged = df["converged"].sum()
                st.metric(
                    "Converged", f"{converged} ({100*converged/len(df):.1f}%)"
                )
            with col3:
                two_phase = ((df["beta"] > 0.01) & (df["beta"] < 0.99)).sum()
                st.metric("Two-Phase Points", two_phase)

            # Data table
            with st.expander("📊 View Data Table"):
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False)
                st.download_button(
                    "💾 Download CSV",
                    csv,
                    "flash_grid_results.csv",
                    "text/csv",
                )

            # Visualization
            st.subheader("Phase-y Fraction (β) Map")

            if n_components == 2:
                # Create heatmap for binary systems
                pivot_df = df.pivot(index="T", columns="z_1", values="beta")

                fig = go.Figure(
                    data=go.Heatmap(
                        z=pivot_df.values,
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        colorscale="Viridis",
                        colorbar=dict(title="β"),
                    )
                )

                fig.update_layout(
                    title="Phase-y Fraction (β) Map",
                    xaxis_title=f"Mole Fraction {component_names[0]}",
                    yaxis_title="Temperature [K]",
                    template="plotly_white",
                    height=500,
                )

                st.plotly_chart(fig, use_container_width=True)

            # K-values plot
            st.subheader("K-values vs Temperature")

            fig = go.Figure()

            for i in range(n_components):
                df[f"K_{i+1}"] = df[f"y_{i+1}"] / df[f"x_{i+1}"]

                fig.add_trace(
                    go.Scatter(
                        x=df["T"],
                        y=df[f"K_{i+1}"],
                        mode="markers",
                        name=f"K-{component_names[i]}",
                        marker=dict(size=4),
                    )
                )

            fig.add_hline(y=1.0, line_dash="dash", line_color="gray")

            fig.update_layout(
                title="K-values (y/x)",
                xaxis_title="Temperature [K]",
                yaxis_title="K-value",
                yaxis_type="log",
                template="plotly_white",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

    # =========================================================================
    # ISOTHERMAL PATH MODE
    # =========================================================================
    else:  # Isothermal Path
        st.header("Isothermal Composition Path")
        st.info(
            "Calculate flash along a composition path at constant temperature"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Starting Composition")
            z_start = []
            for i, comp in enumerate(config.components):
                val = st.number_input(
                    f"{comp.name}",
                    value=1.0 if i == 0 else 0.0,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.1,
                    key=f"path_start_{i}",
                )
                z_start.append(val)

            z_start = np.array(z_start)
            z_start = z_start / np.sum(z_start)

        with col2:
            st.subheader("Ending Composition")
            z_end = []
            for i, comp in enumerate(config.components):
                val = st.number_input(
                    f"{comp.name}",
                    value=0.0 if i == 0 else 1.0,
                    min_value=0.0,
                    max_value=1.0,
                    step=0.1,
                    key=f"path_end_{i}",
                )
                z_end.append(val)

            z_end = np.array(z_end)
            z_end = z_end / np.sum(z_end)

        col1, col2 = st.columns(2)

        with col1:
            temperature = st.number_input(
                "Temperature [K]",
                value=298.15,
                min_value=100.0,
                max_value=1000.0,
                step=1.0,
            )

        with col2:
            n_points = st.slider("Number of points", 10, 100, 50)

        if st.button("🔬 Calculate Path", type="primary", key="calc_path"):
            with st.spinner(f"Calculating {n_points} points along path..."):
                alphas = np.linspace(0, 1, n_points)
                z_points = [
                    alpha * z_end + (1 - alpha) * z_start for alpha in alphas
                ]
                z_points = [z / np.sum(z) for z in z_points]

                results = []
                progress_bar = st.progress(0)

                for idx, z in enumerate(z_points):
                    result = flash_ge_single(model, z, temperature)

                    row = {"alpha": alphas[idx], "T": temperature}
                    for i in range(n_components):
                        row[f"z_{i+1}"] = z[i]
                        row[f"x_{i+1}"] = result["x"][i]
                        row[f"y_{i+1}"] = result["y"][i]

                    row["beta"] = result["beta"]
                    row["converged"] = result["converged"]

                    results.append(row)
                    progress_bar.progress((idx + 1) / n_points)

                st.session_state.path_results = pd.DataFrame(results)
                progress_bar.empty()
                st.success("✅ Path calculation complete!")

        # Display path results
        if "path_results" in st.session_state:
            st.markdown("---")
            st.header("Results")

            df = st.session_state.path_results

            # Phase diagram
            st.subheader("Phase Diagram (Txy-like)")

            fig = go.Figure()

            # Plot each component
            for i in range(n_components):
                # Liquid phase
                fig.add_trace(
                    go.Scatter(
                        x=df[f"x_{i+1}"],
                        y=df["alpha"],
                        mode="lines",
                        name=f"{component_names[i]} (liquid)",
                        line=dict(width=2),
                    )
                )

                # Phase-y
                fig.add_trace(
                    go.Scatter(
                        x=df[f"y_{i+1}"],
                        y=df["alpha"],
                        mode="lines",
                        name=f"{component_names[i]} (vapor)",
                        line=dict(dash="dash", width=2),
                    )
                )

            fig.update_layout(
                title=f"Phase Diagram at T = {temperature:.2f} K",
                xaxis_title="Mole Fraction",
                yaxis_title="Path Parameter (α)",
                template="plotly_white",
                height=500,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Phase-y fraction profile
            st.subheader("Phase-y Fraction Profile")

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df["alpha"],
                    y=df["beta"],
                    mode="lines+markers",
                    line=dict(width=2),
                    marker=dict(size=4),
                )
            )

            fig.update_layout(
                title="Phase-y Fraction along Path",
                xaxis_title="Path Parameter (α)",
                yaxis_title="Phase-y Fraction (β)",
                template="plotly_white",
                height=400,
            )

            st.plotly_chart(fig, use_container_width=True)

            # Data table
            with st.expander("📊 View Data Table"):
                st.dataframe(df, use_container_width=True)

                csv = df.to_csv(index=False)
                st.download_button(
                    "💾 Download CSV",
                    csv,
                    "flash_path_results.csv",
                    "text/csv",
                )
