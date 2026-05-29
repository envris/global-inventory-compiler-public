"""Definition of a generic id field that can be used for any identifier type."""

from .chemical_name import ChemicalNameField


class GenericID1Field(ChemicalNameField):
    """See base class Field for documentation of methods and attributes."""

    name = "generic_id_1"
    description = "Generic Identifier 1 (for any identifier type)"


class GenericID2Field(ChemicalNameField):
    """See base class Field for documentation of methods and attributes."""

    name = "generic_id_2"
    description = "Generic Identifier 2 (for any identifier type)"


class GenericID3Field(ChemicalNameField):
    """See base class Field for documentation of methods and attributes."""

    name = "generic_id_3"
    description = "Generic Identifier 3 (for any identifier type)"


class GenericID4Field(ChemicalNameField):
    """See base class Field for documentation of methods and attributes."""

    name = "generic_id_4"
    description = "Generic Identifier 4 (for any identifier type)"


class GenericID5Field(ChemicalNameField):
    """See base class Field for documentation of methods and attributes."""

    name = "generic_id_5"
    description = "Generic Identifier 5 (for any identifier type)"
