"""Definition of a InChI"""

from rdkit import Chem, RDLogger

from . import Field, ValidationError

# Disable RDKit warnings
RDLogger.DisableLog("rdApp.*")  # type: ignore


class InChIField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "inchi"
    dtype = str
    description = "IUPAC International Chemical Identifier (InChI)"
    is_identifier = False
    derived_from = "rdk_mol"

    @staticmethod
    def validate(value: str) -> bool:
        mol = Chem.MolFromInchi(value)
        if mol is None:
            raise ValidationError("Invalid InChI string")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value):
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value):
        return Chem.MolToInchi(required_value)
