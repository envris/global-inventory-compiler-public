"""List of recognised GHS codes"""

ghs_code_choices = {
    # Environmental hazards
    "H400",
    "H401",
    "H402",
    "H410",
    "H411",
    "H412",
    "H413",
    "H420",
    # EU-specific environmental hazards
    "EUH059",
    "EUH430",
    "EUH431",
    "EUH440",
    "EUH441",
    "EUH450",
    "EUH451",
    # Explosives
    "H200",
    "H201",
    "H202",
    "H203",
    "H204",
    "H205",
    # Flammable gases
    "H220",
    "H232",
    "H230",
    "H231",
    "H221",
    # Aerosols
    "H222",
    "H223",
    "H229",
    # Oxidizing gases
    "H270",
    # Gases under pressure
    "H280",
    "H280a",
    "H280b",
    "H280c",
    "H281",
    # Flammable liquids
    "H224",
    "H225",
    "H226",
    "H227",
    # Flammable solids
    "H228",
    # Self-reactive substances and mixtures
    "H240",
    "H241",
    "H242",
    # Pyrophoric liquids/solids
    "H250",
    # Self heating substances and mixtures
    "H251",
    "H252",
    # Substances and mixtures which, in contact with water, emit flammable gases
    "H260",
    "H261",
    # Oxidizing liquids/solids
    "H271",
    "H272",
    # Corrosive to metals
    "H290",
    # Desensitized explosives
    "H206",
    "H207",
    "H208",
    # Australia-specific physical hazards
    "AUH001",
    "AUH006",
    "AUH014",
    "AUH018",
    "AUH019",
    "AUH044",
    # EU-specific physical hazards
    "EUH001",
    "EUH006",
    "EUH014",
    "EUH018",
    "EUH019",
    "EUH044",
    # Acute toxicity - cat 1 and 2
    "H300",
    "H310",
    "H330",
    # Acute toxicity - cat 3
    "H301",
    "H311",
    "H331",
    # Acute toxicity - cat 4
    "H302",
    "H312",
    "H332",
    # Acute toxicity - cat 5
    "H303",
    "H313",
    "H333",
    # Skin corrosion/irritation
    "H314",
    "H315",
    "H316",
    # Serious eye damage/eye irritation
    "H318",
    "H319",
    "H320",
    # Respiratory sensitizer
    "H334",
    # Skin sensitizer
    "H317",
    # Germ cell mutagenicity
    "H340",
    "H341",
    # Carcinogenicity
    "H350",
    "H351",
    # Reproductive toxicity
    "H360",
    "H361",
    "H362",
    # Specific target organ toxicity - single exposure
    "H370",
    "H371",
    "H335",
    "H336",
    # Specific target organ toxicity - repeated exposure
    "H372",
    "H373",
    # Aspiration hazard
    "H304",
    "H305",
    # Health hazards with letters added at end of code
    "H350i",
    "H360D",
    "H360F",
    "H360FD",
    "H360Fd",
    "H360Df",
    "H361d",
    "H361f",
    "H361fd",
    # EU-specific health hazards
    "EUH029",
    "EUH031",
    "EUH032",
    "EUH066",
    "EUH070",
    "EUH071",
    "EUH380",
    "EUH381",
    "EUH201",
    "EUH201A",
    "EUH202",
    "EUH203",
    "EUH204",
    "EUH205",
    "EUH206",
    "EUH207",
    "EUH208",
    "EUH209",
    "EUH209A",
    "EUH210",
    "EUH211",
    "EUH401",
    # Australia-specific health hazards
    "AUH029",
    "AUH031",
    "AUH032",
    "AUH066",
    "AUH070",
    "AUH071",
}


def is_recognised_ghs_code(code: str) -> bool:
    """Return True if code is in the recognised GHS code choices"""
    return code in ghs_code_choices
