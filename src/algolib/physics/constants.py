# algolib/physics/constants.py
"""
CODATA-based physical constants in SI units.

Notes
-----
- All values are provided in SI base units.
- `rel_unc` is the relative standard uncertainty. A value of `0.0` indicates an
   exact value as defined by the 2019 SI redefinition (e.g., `c`, `h`, `e`,
   `k_B`, `N_A`).
- Source label reflects the CODATA release used to curate the numbers.
"""

CODATA_VINTAGE = "CODATA 2022"

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PhysConst:
    r"""
    Container for a physical constant in SI units.
        
    Attributes
    ----------
    value : float
        Numerical value in SI base units.
    unit : str
        Unit string, e.g. "m s^-1", "J s", "C".
    rel_unc : float | None
        Relative standard uncertainty (e.g. ``1.5e-10``); use ``0.0`` for
        exact constants per the 2019 SI definitions.
    source : str
        Provenance label, e.g. "CODATA 2022".
    symbol : str
        Conventional symbol such as ``c``, ``h``, ``k_B``.
    """
    value: float            # numerical value (SI base units)
    unit: str               # unit string, e.g. "m s^-1"
    rel_unc: float | None   # relative uncertainty (0.0 for exact constants)
    source: str             # provenance label, e.g. "CODATA 2022"
    symbol: str             # conventional symbol ("c", "h", etc.)



# — SI defining constants (exact since the 2019 redefinition) —

c   = PhysConst(299792458,               "m s^-1",   0.0,          "CODATA 2022", "c")
h   = PhysConst(6.62607015e-34,          "J s",      0.0,          "CODATA 2022", "h")
e   = PhysConst(1.602176634e-19,         "C",        0.0,          "CODATA 2022", "e")
k_B = PhysConst(1.380649e-23,            "J K^-1",   0.0,          "CODATA 2022", "k_B")
N_A = PhysConst(6.02214076e23,           "mol^-1",   0.0,          "CODATA 2022", "N_A")

# Common derived/experimental constants (some with nonzero uncertainty; values shown as examples)
hbar = PhysConst(1.054571817e-34,        "J s",      0.0,          "CODATA 2022", "ħ")   # derived as h / (2π); exact by definition
R    = PhysConst(8.314462618,            "J mol^-1 K^-1", 0.0,     "CODATA 2022", "R")   # R = N_A * k_B (exact by definition)

# Examples with nonzero uncertainties (values are placeholders until a CODATA vintage is chosen)
alpha   = PhysConst(7.2973525643e-3,     "1",       1.6e-10,     "CODATA 2022", "α")
m_e     = PhysConst(9.1093837139e-31,    "kg",      3.1e-10,     "CODATA 2022", "m_e")
m_p     = PhysConst(1.67262192595e-27,   "kg",      3.1e-10,     "CODATA 2022", "m_p")
m_n     = PhysConst(1.67492750056e-27,   "kg",      5.1e-10,     "CODATA 2022", "m_n")
m_u     = PhysConst(1.66053906892e-27,   "kg",      3.1e-10,     "CODATA 2022", "m_u")  # defined as 1/12 of the mass of a 12C atom (not exact after 2019 SI)

R_inf   = PhysConst(1.0973731568157e7,   "m^-1",    1.1e-12,     "CODATA 2022", "R_∞")
a0      = PhysConst(5.29177210544e-11,   "m",       1.6e-10,     "CODATA 2022", "a0")
sigmaSB = PhysConst(5.670374419e-8,      "W m^-2 K^-4", 1.5e-6,  "CODATA 2022", "σ")

# Note: After the 2019 SI redefinition, μ0 and ε0 are not exact. Prefer deriving them from α, h, c, and e; do not hard-code as exact.