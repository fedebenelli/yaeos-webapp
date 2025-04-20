import yaeos


AR_MODELS = {
    "PengRobinson76": {"setter": yaeos.PengRobinson76},
    "PengRobinson78": {"setter": yaeos.PengRobinson78},
    "SoaveRedlichKwong": {"setter": yaeos.SoaveRedlichKwong},
    # "RKPR": {"setter": yaeos.RKPR},
    # "PSRK": {"setter": yaeos.PSRK},
}

GE_MODELS = {
    "UNIFAC_VLE": {"setter": yaeos.UNIFACVLE},
    "NRTL": {"setter": yaeos.NRTL},
}