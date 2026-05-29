"""Test cases for RDKMolField."""

from rdkit import Chem

from gic.fields import FieldTestCases
from gic.fields.rdk_mol import RDKMolField


def csmiles(smiles: str) -> str:
    """Canonicalise a SMILES string using RDKit."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string: {smiles}")
    return Chem.MolToSmiles(mol)


rdk_mol_test_cases = FieldTestCases(
    valid=[],
    invalid=[],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[
        # Round-trip deserialise checks, factoring in canonicalisation by RDKit
        ("C(=N)(N)N.Cl", csmiles("C(=N)(N)N.Cl")),
        ("C1=CC(=C(C(=C1)Cl)C(=O)O)Cl", csmiles("C1=CC(=C(C(=C1)Cl)C(=O)O)Cl")),
        ("C1=CC(=C(C(=C1Cl)C(=O)O)Cl)Cl", csmiles("C1=CC(=C(C(=C1Cl)C(=O)O)Cl)Cl")),
        ("CC(C(=O)O)O", csmiles("CC(C(=O)O)O")),
        ("C1CNP(=O)(OC1)N(CCCl)CCCl", csmiles("C1CNP(=O)(OC1)N(CCCl)CCCl")),
    ],
    generated=[
        ("C(=N)(N)N.Cl", csmiles("C(=N)(N)N.Cl")),
        ("C1=CC(=C(C(=C1)Cl)C(=O)O)Cl", csmiles("C1=CC(=C(C(=C1)Cl)C(=O)O)Cl")),
    ],
)


def test_rdkmol_field():
    """Test RDKMolField with predefined test cases."""
    field = RDKMolField()
    field.test(rdk_mol_test_cases)
