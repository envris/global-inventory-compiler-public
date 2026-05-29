"""Definition of a SMILES"""

from rdkit import Chem, RDLogger

from . import Field, ValidationError

# Disable RDKit warnings
RDLogger.DisableLog("rdApp.*")  # type: ignore


class SMILESField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "smiles"
    dtype = str
    description = "Simplified Molecular Input Line Entry System (SMILES)"
    is_identifier = False
    derived_from = None

    @staticmethod
    def validate(value: str) -> bool:
        mol = Chem.MolFromSmiles(value)
        if mol is None:
            raise ValidationError("Invalid SMILES string")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value):
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value):
        raise NotImplementedError("generate method not defined for SMILES field")
