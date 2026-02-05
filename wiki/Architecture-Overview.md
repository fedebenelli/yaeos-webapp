# Architecture Overview

YaEoS WebApp is a modular web application built using **Streamlit** that serves as a frontend for the **yaeos** (Yet Another Equation of State) thermodynamic library.

## 🏗️ High-Level Design

The application follows a standard **Model-View-Controller (MVC)**-like pattern adapted for Streamlit:

*   **Model**: The `yaeos` library and the `models/` directory define the thermodynamic logic.
*   **View**: Streamlit pages (`home.py`, `flash_ge.py`, etc.) and `ui_components.py` handle the UI rendering.
*   **Controller**: `app.py` acts as the main controller, managing navigation and global configuration state.

## 📂 Project Structure

```text
thermo-gui/
├── app.py                  # Entry point & Main Controller
├── home.py                 # Home page content
├── flash_ge.py             # Logic & UI for Flash calculations (GeModel)
├── phase_envelope.py       # Logic & UI for Phase Envelopes (ArModel)
├── gpec.py                 # Logic & UI for GPEC diagrams (ArModel)
├── model_setup.py          # UI for configuring thermodynamic models
├── ui_components.py        # Reusable UI widgets (e.g., Matrix inputs)
├── thermo_utils.py         # Data structures (ComponentData)
├── models/                 # Thermodynamic Model definitions
│   ├── residual_helmholtz/ # ArModel (Cubic EoS, Mixing Rules)
│   └── excess_gibbs/       # GeModel (Activity Coefficients)
└── requirements.txt        # Python dependencies
```

## 🔑 Key Components

### 1. The Main Controller (`app.py`)
*   Initializes the application layout.
*   Manages the Sidebar navigation.
*   Instantiates the global `EOSModelConfig`.
*   Routes the user to the selected page function.

### 2. Configuration Manager (`EOSModelConfig`)
Located in `app.py`, this class is the "source of truth" for the current session. It stores:
*   Selected model type (e.g., Peng-Robinson, NRTL).
*   List of components and their properties.
*   Model interactions patterns (Mixing Rules).

### 3. Calculation Pages (`flash_ge.py`, etc.)
Each calculation page is self-contained. It:
1.  **Validates** that a valid model exists in the session state.
2.  **Collects** run-specific parameters (e.g., Temperature, Composition grid).
3.  **Calls** the underlying `yaeos` model methods.
4.  **Visualizes** the results using Plotly.

## 💻 Tech Stack

*   **Frontend/App Framework**: [Streamlit](https://streamlit.io/)
*   **Thermodynamics Engine**: `yaeos` (Python + Fortran)
*   **Visualization**: [Plotly Graph Objects](https://plotly.com/python/graph-objects/)
*   **Data Manipulation**: `pandas`, `numpy`
