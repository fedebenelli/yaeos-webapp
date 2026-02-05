# Extending the Application

One of the key strengths of YaEoS WebApp is its extensibility. This guide explains how to add new models, components, and pages.

## ➕ Adding a New Thermodynamic Model

The application uses a **Registry Pattern** to discover available models. To add a new EoS or Activity Coefficient model:

### 1. Implement the Model Class
Create your model class in the `models/` directory. It should implement the standard interface expected by `yaeos`.

### 2. Register the Model
Add your class to the appropriate registry in `models/__init__.py` or the relevant submodule.

**Example for a new Cubic EoS:**

```python
# models/residual_helmholtz/custom_eos.py
from . import CUBIC_EOS_REGISTRY

class MyNewEOS:
    @classmethod
    def get_display_name(cls):
        return "My Custom EoS"
    
    # ... implementation ...

# Register it (automatically picked up by model_setup.py)
CUBIC_EOS_REGISTRY["MyNewEOS"] = MyNewEOS
```

Once registered, it will automatically appear in the dropdown menu on the **Model Configuration** page.

## 🔌 Adding a New Mixing Rule

Mixing rules follow a similar pattern found in `models/residual_helmholtz/cubic/mixing_rules.py`.

1.  Create a class implementing the mixing rule strategy.
2.  Register it in `MIXING_RULE_REGISTRY`.
3.  Implement `setup_ui()` to define how users input its parameters (e.g., interaction matrices).

## 📄 Adding a New Page

To add a new calculation module (e.g., "Critical Point Finder"):

1.  **Create the Module**: Create a new file (e.g., `critical_point.py`).
2.  **Define the UI Function**: Create a main function, e.g., `show_critical_point_page()`.
3.  **Register Navigation**: Open `app.py` and add your page to the navigation list:

```python
# app.py

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        # ...
        "Critical Point Finder",  # <--- Add this
    ],
)

if page == "Critical Point Finder":
    from critical_point import show_critical_point_page
    show_critical_point_page()
```

## 🛠️ Reusing UI Components

Use `ui_components.py` to maintain UI consistency.

*   `create_parameter_matrix()`: Use this for any $N \times N$ interaction parameter input. It handles symmetry, Excel pasting, and validation automatically.
*   `input_basic_component_properties()`: Use for component data entry.
