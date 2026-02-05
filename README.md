# YAEOS Web App

A modern web interface for **YAEOS (Yet Another Equation of State)**, a Python/Fortran library for advanced thermodynamic calculations.

This application provides an intuitive graphical interface to configure thermodynamic models, perform flash calculations, and visualize complex phase behaviors like phase envelopes and GPEC diagrams.

## 🚀 Features

- **Model Configuration**: Easily configure **ArModel** (Residual Helmholtz) and **GeModel** (Excess Gibbs) systems.
- **Phase Envelopes**: Calculate and visualize PT diagrams and vapor-liquid equilibrium boundaries.
- **GPEC Diagrams**: Generate Global Phase Equilibrium Calculation diagrams for binary systems (Pxy, Txy, Critical Locus).
- **Flash Calculations**: Perform isothermal flash calculations (Single Point, Grid, and Path) using GeModels.
- **Interactive Visualization**: Rich, interactive plots using [Plotly](https://plotly.com/).

## 🛠️ Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd thermo-gui
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🖥️ Usage

1.  **Run the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

2.  **Navigate the interface**:
    -   **Home**: Overview and quick start guide.
    -   **Model Configuration**: Define your components and model type (e.g., Peng-Robinson, NRTL).
    -   **Phase Envelope**: Generate PT diagrams (Requires ArModel).
    -   **GPEC Diagram**: Analyze binary system global phase behavior (Requires ArModel).
    -   **FlashT (GeModel)**: Perform flash calculations for activity coefficient models.

## 📂 Project Structure

-   `app.py`: Main application entry point and global state management.
-   `models/`: Core thermodynamic model definitions.
-   `ui_components.py`: Reusable UI widgets and helper functions.
-   `flash_ge.py`: Flash calculation logic and UI.
-   `phase_envelope.py`: Phase envelope calculation logic.
-   `gpec.py`: GPEC diagram logic.

## 📦 Requirements

-   Python 3.8+
-   yaeos
-   streamlit
-   plotly
-   pandas
-   numpy

## License

[Insert License Here]
