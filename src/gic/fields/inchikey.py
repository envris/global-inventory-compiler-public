"""Definition of InChIKey field"""

import re

from rdkit import Chem
from rdkit.RDLogger import DisableLog  # type: ignore

from . import Field, ValidationError

# Disable RDKit warnings
DisableLog("rdApp.*")


_inchikey_re = re.compile(r"^[A-Z]{14}-[A-Z]{8}[SN]A-[A-Z]$")


class InChIKeyField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "inchikey"
    dtype = str
    description = "International Chemical Identifier Key (InChIKey) string"
    is_identifier = True
    derived_from = "rdk_mol"

    @staticmethod
    def validate(value) -> bool:
        if not _inchikey_re.match(value):
            raise ValidationError("Invalid format")
        return True

    @staticmethod
    def has_format(value: str) -> bool:
        return _inchikey_re.match(value) is not None

    @staticmethod
    def patch(value):
        raise NotImplementedError("patch method not defined for this field")

    @staticmethod
    def generate(required_value: Chem.Mol) -> str:
        return Chem.MolToInchiKey(required_value)
