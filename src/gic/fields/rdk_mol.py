"""Definition of RDKit Mol field"""

from typing import Any

from rdkit import Chem, RDLogger

from . import Field

# Disable RDKit warnings
RDLogger.DisableLog("rdApp.*")  # type: ignore


class RDKMolField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "rdk_mol"
    dtype = Chem.Mol
    description = "RDKit Mol object"
    is_identifier = False
    derived_from = "smiles"

    @staticmethod
    def validate(value: Chem.Mol) -> bool:
        # Type check is sufficient
        raise NotImplementedError("validate method not defined for RDKMol field")

    @staticmethod
    def has_format(value: Chem.Mol) -> bool:
        raise NotImplementedError("has_format method not defined for RDKMol field")

    @staticmethod
    def patch(value: Any) -> Any:
        """Deserialise a SMILES string into an RDKit Mol object."""
        if isinstance(value, str):
            mol = Chem.MolFromSmiles(value)
            if mol:
                return mol
        return value

    @staticmethod
    def generate(required_value: str) -> Chem.Mol:
        """Generate an RDKit Mol object from a SMILESField."""
        mol = Chem.MolFromSmiles(required_value)
        if mol is None:
            raise ValueError(
                "Invalid SMILES provided to generate RDKit Mol. This "
                "should not happen if the SMILESField is validated correctly."
            )
        return mol

    @staticmethod
    def serialise(value: Chem.Mol) -> str:
        """Serialise RDKit Mol to a SMILES string."""
        return Chem.MolToSmiles(value)
