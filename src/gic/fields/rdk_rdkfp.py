"""Definition of RDKit RDK Fingerprint field"""

from typing import Any

from rdkit import Chem, RDLogger
from rdkit.DataStructs.cDataStructs import ExplicitBitVect

from . import Field

# Disable RDKit warnings
RDLogger.DisableLog("rdApp.*")  # type: ignore


class RDKitRDKFingerprintField(Field):
    """See base class Field for documentation of methods and attributes."""

    name = "rdk_rdkfp"
    dtype = ExplicitBitVect
    description = "RDKit RDK Fingerprint"
    is_identifier = False
    derived_from = "rdk_mol"

    @staticmethod
    def validate(value) -> bool:
        # Type checking is sufficient
        raise NotImplementedError("validate method not defined for this field")

    @staticmethod
    def has_format(value: str) -> bool:
        raise NotImplementedError("has_format method not defined for this field")

    @staticmethod
    def patch(value: Any) -> Any:
        """Deserialise a Base64-encoded fingerprint into an ExplicitBitVect."""
        if not isinstance(value, str):
            return value
        fingerprint = ExplicitBitVect(2048)
        try:
            fingerprint.FromBase64(value)
        except (RuntimeError, ValueError):
            return value
        return fingerprint

    @staticmethod
    def generate(required_value: Chem.Mol) -> ExplicitBitVect:
        """Generate an RDKit RDK fingerprint from an RDKit Mol object."""
        return Chem.RDKFingerprint(required_value)

    @staticmethod
    def serialise(value: ExplicitBitVect) -> str:
        """Serialise RDKit fingerprint to a base64 string."""
        return value.ToBase64()
