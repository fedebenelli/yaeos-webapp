from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ComponentData:
    """Component thermodynamic data"""

    name: str
    tc: float  # Critical temperature [K]
    pc: float  # Critical pressure [bar]
    w: float  # Acentric factor
    zc: Optional[float] = None  # Critical compressibility (for RKPR)
    c1: Optional[float] = None  # Mathias-Copeman parameter (for PSRK)
    c2: Optional[float] = None  # Mathias-Copeman parameter (for PSRK)
    c3: Optional[float] = None  # Mathias-Copeman parameter (for PSRK)
    groups: Optional[Dict[int, int]] = None  # UNIFAC groups (for PSRK)
