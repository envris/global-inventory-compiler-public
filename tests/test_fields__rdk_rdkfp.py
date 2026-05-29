"""Test cases for RDKit RDK Fingerprint field"""

from rdkit import Chem

from gic.fields import FieldTestCases
from gic.fields.rdk_rdkfp import RDKitRDKFingerprintField


def base64_fp(smiles: str) -> str:
    """Generate RDKit RDK fingerprint as a base64 string from a SMILES string."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    fp = Chem.RDKFingerprint(mol)
    return fp.ToBase64()


def rdk_mol(smiles: str) -> Chem.Mol:
    """Generate an RDKit Mol object from a SMILES string."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    return mol


rdk_rdkfp_test_cases = FieldTestCases(
    valid=[],
    invalid=[],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[
        # Round-trip deserialise checks
        (base64_fp("C(=N)(N)N.Cl"), base64_fp("C(=N)(N)N.Cl")),
        (base64_fp("CC(C(=O)O)O"), base64_fp("CC(C(=O)O)O")),
    ],
    generated=[
        (rdk_mol("C(=N)(N)N.Cl"), base64_fp("C(=N)(N)N.Cl")),
        (
            rdk_mol("C1=CC(=C(C(=C1)Cl)C(=O)O)Cl"),
            base64_fp("C1=CC(=C(C(=C1)Cl)C(=O)O)Cl"),
        ),
    ],
)


def test_rdk_rdkfp_field():
    """Test the RDKit RDK Fingerprint field with predefined test cases"""
    field = RDKitRDKFingerprintField()
    field.test(rdk_rdkfp_test_cases)
