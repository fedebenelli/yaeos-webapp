import yaeos

import numpy as np

import pandas as pd

import streamlit as st

from collections import OrderedDict

from setters import setup_nrtl


AR_MODELS = {
    "PengRobinson76": {"setter": yaeos.PengRobinson76},
    "PengRobinson78": {"setter": yaeos.PengRobinson78},
    "SoaveRedlichKwong": {"setter": yaeos.SoaveRedlichKwong},
    "RKPR": {"setter": yaeos.RKPR},
    # "PSRK": {"setter": yaeos.PSRK},
}

AR_MIXING_RULES = {
    "QMR": {"setter": yaeos.QMR},
    "QMRTD": {"setter": yaeos.QMRTD},
    "MHV1": {"setter": yaeos.MHV},
    "HV": {"setter": yaeos.HV},
}

GE_MODELS = {
    "NRTL": {"setter": setup_nrtl},
    # "UNIFAC_VLE": {"setter": yaeos.UNIFACVLE},
}
