import streamlit as st
import numpy as np
import pandas as pd
from typing import List, Optional

# ==============================================================================
# UI Helper Functions for Matrix Parameters
# ==============================================================================


def create_parameter_matrix(
    n_components: int,
    component_names: List[str],
    matrix_name: str,
    default_value: float = 0.0,
    symmetric: bool = True,
    key_prefix: str = "matrix",
    help_text: str = "",
) -> np.ndarray:
    """
    Create an interactive matrix input for binary interaction parameters.

    Parameters
    ----------
    n_components : int
        Number of components in the system
    component_names : List[str]
        Names of the components
    matrix_name : str
        Name of the matrix (e.g., "kij", "lij", "aij")
    default_value : float, optional
        Default value for off-diagonal elements
    symmetric : bool, optional
        Whether the matrix is symmetric (default: True)
    key_prefix : str, optional
        Prefix for Streamlit widget keys to avoid conflicts
    help_text : str, optional
        Help text to display above the matrix

    Returns
    -------
    np.ndarray
        The constructed parameter matrix
    """
    matrix = np.zeros((n_components, n_components))

    if help_text:
        st.write(help_text)

    # Input mode selection
    input_mode = st.radio(
        f"Input mode for {matrix_name}",
        ["Manual Entry", "Paste from Excel"],
        key=f"{key_prefix}_{matrix_name}_input_mode",
        horizontal=True,
    )

    if input_mode == "Paste from Excel":
        matrix = paste_matrix_from_excel(
            n_components=n_components,
            component_names=component_names,
            matrix_name=matrix_name,
            symmetric=symmetric,
            key_prefix=key_prefix,
            default_value=default_value,
        )
    else:
        # Manual entry mode
        st.write(f"**{matrix_name} Matrix:**")

        if symmetric and n_components == 2:
            # For binary systems with symmetric matrices, show only one value
            key = f"{key_prefix}_{matrix_name}_0_1"
            value = st.number_input(
                f"{matrix_name}₁₂ ({component_names[0]}-{component_names[1]})",
                value=default_value,
                step=0.01,
                format="%.4f",
                key=key,
                help=f"Binary interaction parameter between {component_names[0]} and {component_names[1]}",
            )
            matrix[0, 1] = value
            matrix[1, 0] = value  # Mirror for symmetry

        elif symmetric:
            # For symmetric matrices with 3+ components, show upper triangle
            for i in range(n_components):
                cols = st.columns(n_components)
                for j in range(n_components):
                    with cols[j]:
                        if i < j:
                            # Upper triangle: input field
                            key = f"{key_prefix}_{matrix_name}_{i}_{j}"
                            value = st.number_input(
                                f"{component_names[i]}-{component_names[j]}",
                                value=default_value,
                                step=0.01,
                                format="%.4f",
                                key=key,
                            )
                            matrix[i, j] = value
                            matrix[j, i] = value  # Mirror to lower triangle
                        elif i == j:
                            # Diagonal: display only
                            st.text("0.0000")
                        else:
                            # Lower triangle: display mirrored value
                            st.text(f"{matrix[i, j]:.4f}")
        else:
            # For non-symmetric matrices, show all elements
            if n_components == 2:
                # For binary non-symmetric, show two values in a cleaner layout
                col1, col2 = st.columns(2)
                with col1:
                    key_12 = f"{key_prefix}_{matrix_name}_0_1"
                    value_12 = st.number_input(
                        f"{matrix_name}₁₂ ({component_names[0]}→{component_names[1]})",
                        value=default_value,
                        step=0.01,
                        format="%.4f",
                        key=key_12,
                    )
                    matrix[0, 1] = value_12

                with col2:
                    key_21 = f"{key_prefix}_{matrix_name}_1_0"
                    value_21 = st.number_input(
                        f"{matrix_name}₂₁ ({component_names[1]}→{component_names[0]})",
                        value=default_value,
                        step=0.01,
                        format="%.4f",
                        key=key_21,
                    )
                    matrix[1, 0] = value_21
            else:
                # For 3+ components, show full matrix grid
                for i in range(n_components):
                    cols = st.columns(n_components)
                    for j in range(n_components):
                        with cols[j]:
                            if i != j:
                                key = f"{key_prefix}_{matrix_name}_{i}_{j}"
                                value = st.number_input(
                                    f"{component_names[i]}-{component_names[j]}",
                                    value=default_value,
                                    step=0.01,
                                    format="%.4f",
                                    key=key,
                                )
                                matrix[i, j] = value
                            else:
                                # Diagonal
                                st.text("0.0000")

    return matrix


def paste_matrix_from_excel(
    n_components: int,
    component_names: List[str],
    matrix_name: str,
    symmetric: bool,
    key_prefix: str,
    default_value: float = 0.0,
) -> np.ndarray:
    """
    Create a matrix by pasting data from Excel.

    Parameters
    ----------
    n_components : int
        Number of components
    component_names : List[str]
        Names of components
    matrix_name : str
        Name of the matrix
    symmetric : bool
        Whether the matrix is symmetric
    key_prefix : str
        Key prefix for widgets
    default_value : float
        Default value for the matrix

    Returns
    -------
    np.ndarray
        The parameter matrix
    """
    st.write(f"**Paste {matrix_name} Matrix from Excel:**")

    # Initialize matrix in session state if not present
    session_key = f"{key_prefix}_{matrix_name}_pasted_matrix"
    if session_key not in st.session_state:
        st.session_state[session_key] = np.full(
            (n_components, n_components), default_value
        )
        np.fill_diagonal(st.session_state[session_key], 0.0)

    # Check if matrix size has changed (components added/removed)
    if st.session_state[session_key].shape != (n_components, n_components):
        st.session_state[session_key] = np.full(
            (n_components, n_components), default_value
        )
        np.fill_diagonal(st.session_state[session_key], 0.0)

    # Show format information
    with st.expander("ℹ️ How to paste matrix data", expanded=False):
        st.markdown(
            f"""
        **Format options:**
        
        1. **Full matrix** ({n_components}×{n_components}):
           - Copy the entire matrix from Excel (including diagonal zeros)
           - Paste in the text area below
        
        2. **Upper triangle only** (for symmetric matrices):
           - Copy only the upper triangle values
           - Values will be mirrored to lower triangle
        
        **Example for {n_components} components:**
        """
        )

        if symmetric and n_components == 3:
            st.code(
                """0.0    0.05    0.03
0.05    0.0     0.02
0.03    0.02    0.0""",
                language=None,
            )
            st.caption("Or just upper triangle:")
            st.code(
                """0.05    0.03
0.02""",
                language=None,
            )
        else:
            example_matrix = np.full((min(n_components, 3), min(n_components, 3)), 0.05)
            np.fill_diagonal(example_matrix, 0.0)
            st.code(
                "\n".join(
                    ["\t".join([f"{val:.2f}" for val in row]) for row in example_matrix]
                ),
                language=None,
            )

    col1, col2 = st.columns([3, 1])

    with col1:
        delimiter_option = st.radio(
            "Delimiter",
            ["Whitespace (Tab/Space)", "Comma"],
            horizontal=True,
            key=f"{key_prefix}_{matrix_name}_delimiter",
        )

        delimiter_map = {
            "Whitespace (Tab/Space)": None,  # None uses split() which handles any whitespace
            "Comma": ",",
        }
        delimiter = delimiter_map[delimiter_option]

    with col2:
        matrix_format = "full"
        if symmetric:
            matrix_format = (
                st.radio(
                    "Format",
                    ["Full", "Upper triangle"],
                    key=f"{key_prefix}_{matrix_name}_format",
                )
                .lower()
                .replace(" ", "_")
            )

    paste_area = st.text_area(
        "Paste matrix data here:",
        height=150,
        placeholder="Paste your matrix data from Excel...",
        key=f"{key_prefix}_{matrix_name}_paste_area",
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button(
            "📥 Import Matrix",
            key=f"{key_prefix}_{matrix_name}_import_btn",
            type="primary",
        ):
            if paste_area.strip():
                try:
                    # Parse pasted data
                    lines = [
                        line.strip()
                        for line in paste_area.strip().split("\n")
                        if line.strip()
                    ]

                    if matrix_format == "upper_triangle" and symmetric:
                        # Parse upper triangle format
                        matrix = parse_upper_triangle_matrix(
                            lines, n_components, delimiter
                        )
                    else:
                        # Parse full matrix format
                        matrix = parse_full_matrix(lines, n_components, delimiter)

                    # Validate matrix
                    if matrix.shape != (n_components, n_components):
                        st.error(
                            f"❌ Matrix size mismatch! Expected {n_components}×{n_components}, got {matrix.shape[0]}×{matrix.shape[1]}"
                        )
                        return st.session_state[session_key]

                    # For symmetric matrices, ensure symmetry
                    if symmetric:
                        matrix = (matrix + matrix.T) / 2

                    # Ensure diagonal is zero
                    np.fill_diagonal(matrix, 0.0)

                    # Store in session state
                    st.session_state[session_key] = matrix

                    st.success(f"✅ Successfully imported {matrix_name} matrix!")

                except Exception as e:
                    st.error(f"❌ Error parsing matrix: {str(e)}")
                    st.info("Please check your data format and delimiter selection.")
            else:
                st.warning("Please paste matrix data first!")

    with col2:
        if st.button(
            "🔄 Reset to Default", key=f"{key_prefix}_{matrix_name}_reset_btn"
        ):
            st.session_state[session_key] = np.full(
                (n_components, n_components), default_value
            )
            np.fill_diagonal(st.session_state[session_key], 0.0)
            st.success("Matrix reset to default values")
            st.rerun()

    # Display current matrix
    st.write("**Current matrix values:**")
    display_matrix_table(st.session_state[session_key], component_names)

    return st.session_state[session_key]


def parse_full_matrix(
    lines: List[str], n_components: int, delimiter: Optional[str]
) -> np.ndarray:
    """
    Parse a full matrix from pasted text.

    Parameters
    ----------
    lines : List[str]
        Lines of text containing matrix data
    n_components : int
        Expected number of components
    delimiter : Optional[str]
        Delimiter to use (None for whitespace)

    Returns
    -------
    np.ndarray
        Parsed matrix
    """
    matrix = np.zeros((n_components, n_components))

    if len(lines) != n_components:
        raise ValueError(f"Expected {n_components} rows, got {len(lines)}")

    for i, line in enumerate(lines):
        # Split by delimiter
        if delimiter is None:
            values = line.split()
        else:
            values = [v.strip() for v in line.split(delimiter) if v.strip()]

        if len(values) != n_components:
            raise ValueError(
                f"Row {i+1}: Expected {n_components} values, got {len(values)}"
            )

        for j, val in enumerate(values):
            matrix[i, j] = float(val.replace(",", "."))

    return matrix


def parse_upper_triangle_matrix(
    lines: List[str], n_components: int, delimiter: Optional[str]
) -> np.ndarray:
    """
    Parse an upper triangle matrix from pasted text.

    Parameters
    ----------
    lines : List[str]
        Lines of text containing matrix data
    n_components : int
        Expected number of components
    delimiter : Optional[str]
        Delimiter to use (None for whitespace)

    Returns
    -------
    np.ndarray
        Parsed symmetric matrix
    """
    matrix = np.zeros((n_components, n_components))

    row = 0
    col = 1

    for line in lines:
        # Split by delimiter
        if delimiter is None:
            values = line.split()
        else:
            values = [v.strip() for v in line.split(delimiter) if v.strip()]

        for val in values:
            if row >= n_components or col >= n_components:
                raise ValueError("Too many values for upper triangle")

            value = float(val.replace(",", "."))
            matrix[row, col] = value
            matrix[col, row] = value  # Mirror to lower triangle

            col += 1
            if col >= n_components:
                row += 1
                col = row + 1

    return matrix


def display_matrix_table(matrix: np.ndarray, component_names: List[str]):
    """
    Display a matrix as a formatted table.

    Parameters
    ----------
    matrix : np.ndarray
        Matrix to display
    component_names : List[str]
        Component names for row/column labels
    """
    import pandas as pd

    # Validate matrix shape matches component names
    if matrix.shape[0] != len(component_names) or matrix.shape[1] != len(
        component_names
    ):
        st.error(
            f"Matrix shape {matrix.shape} doesn't match number of components ({len(component_names)})"
        )
        return

    df = pd.DataFrame(matrix, index=component_names, columns=component_names)

    # Format to 4 decimal places
    st.dataframe(
        df.style.format("{:.4f}").background_gradient(cmap="RdYlGn_r", axis=None),
        use_container_width=True,
    )


def display_matrix_info(matrix_name: str, symmetric: bool = True):
    """
    Display helpful information about the matrix being configured.

    Parameters
    ----------
    matrix_name : str
        Name of the matrix parameter
    symmetric : bool, optional
        Whether the matrix is symmetric
    """
    if symmetric:
        st.info(
            f"ℹ️ {matrix_name} is a **symmetric matrix**. Only the upper triangle needs to be specified."
        )
    else:
        st.info(
            f"ℹ️ {matrix_name} is a **non-symmetric matrix**. All off-diagonal elements must be specified."
        )


def create_nrtl_matrices(
    n_components: int, component_names: List[str], key_prefix: str = "nrtl"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create NRTL parameter matrices (a, b, and alpha).

    NRTL uses: τij = aij + bij/T, with non-randomness parameter αij

    Parameters
    ----------
    n_components : int
        Number of components
    component_names : List[str]
        Names of the components
    key_prefix : str, optional
        Prefix for widget keys

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray]
        The a, b, and alpha matrices
    """
    st.write("**NRTL Parameters:** τij = aij + bij/T")

    # For binary systems, show simplified input
    if n_components == 2:
        st.info(
            "For binary systems, only 4 parameters are needed: a12, a21, b12, b21, and α12"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            a12 = st.number_input("a12", value=0.0, key=f"{key_prefix}_a12")
            a21 = st.number_input("a21", value=0.0, key=f"{key_prefix}_a21")

        with col2:
            b12 = st.number_input("b12 [K]", value=0.0, key=f"{key_prefix}_b12")
            b21 = st.number_input("b21 [K]", value=0.0, key=f"{key_prefix}_b21")

        with col3:
            alpha = st.number_input(
                "α12",
                value=0.3,
                min_value=0.0,
                max_value=1.0,
                step=0.05,
                key=f"{key_prefix}_alpha",
            )

        a = np.array([[0.0, a12], [a21, 0.0]])
        b = np.array([[0.0, b12], [b21, 0.0]])
        c = np.array([[0.0, alpha], [alpha, 0.0]])

    else:
        # For multicomponent systems, use full matrices
        tab1, tab2, tab3 = st.tabs(
            ["aij parameters", "bij parameters [K]", "αij parameters"]
        )

        with tab1:
            display_matrix_info("aij", symmetric=False)
            a = create_parameter_matrix(
                n_components,
                component_names,
                "aij",
                default_value=0.0,
                symmetric=False,
                key_prefix=f"{key_prefix}_a",
            )

        with tab2:
            display_matrix_info("bij", symmetric=False)
            b = create_parameter_matrix(
                n_components,
                component_names,
                "bij",
                default_value=0.0,
                symmetric=False,
                key_prefix=f"{key_prefix}_b",
            )

        with tab3:
            display_matrix_info("αij", symmetric=True)
            c = create_parameter_matrix(
                n_components,
                component_names,
                "αij",
                default_value=0.3,
                symmetric=True,
                key_prefix=f"{key_prefix}_alpha",
            )

    return a, b, c


def input_basic_component_properties(key_prefix: str = "comp") -> tuple:
    """
    Create input fields for basic component properties (Tc, Pc, w).

    Returns
    -------
    tuple
        (name, tc, pc, w)
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        comp_name = st.text_input(
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

    return comp_name, tc, pc, w
