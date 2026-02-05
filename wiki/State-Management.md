# State Management

Effective state management is crucial in Streamlit to persist data between re-runs. YaEoS WebApp uses a hybrid approach:

## 1. The `EOSModelConfig` Class

Defined in `app.py`, this class acts as a strong-typed container for the configuration.

```python
class EOSModelConfig:
    def __init__(self):
        self.components: List[ComponentData] = []
        self.model_category: str = ModelType.RESIDUAL_HELMHOLTZ
        self.model_type: str = "PengRobinson76"
        self.mixing_rule: Optional[MixingRuleStrategy] = None
```

This object is stored in `st.session_state.model_config` and is mutated by the `model_setup.py` page.

## 2. Session State Variables

Key variables reserved in `st.session_state`:

| Key | Type | Description |
| :--- | :--- | :--- |
| `model_config` | `EOSModelConfig` | Stores the user's setup (components, model selection). |
| `model_created` | `bool` | Flag indicating if `model` object is ready for use. |
| `model` | `object` | The actual instantiated `yaeos` backend object (C++ attached). |
| `ge_model_instance` | `object` | Intermediate configuration object for GeModels. |

## 3. Persistent Data Flow

1.  **Configuration**: User interacts with `model_setup.py`. Changes update `st.session_state.model_config`.
2.  **Creation**: When "Create Model" is clicked, the `model` object is instantiated and stored in `st.session_state.model`.
3.  **Calculation**: Pages like `flash_ge.py` read `st.session_state.model` to perform calculations.

> **⚠️ Important**: Any change to `model_config` (e.g., adding a component) invalidates the `model` object. The app handles this by setting `model_created = False`, forcing the user to rebuild the model.
