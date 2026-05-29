"""Test cases for SMILESField."""

from gic.fields import FieldTestCases
from gic.fields.smiles import SMILESField

smiles_test_cases = FieldTestCases(
    valid=[
        "C(=N)(N)N.Cl",
        "C1=CC(=C(C(=C1)Cl)C(=O)O)Cl",
        "C1=CC(=C(C(=C1Cl)C(=O)O)Cl)Cl",
        "C1=CC(=CC=C1C(C2=CC=C(C=C2)Cl)C(Cl)(Cl)Cl)Cl",
        "C1=CC=C2C3=C4C(=CC2=C1)C=CC5=C4C(=CC=C5)C=C3",
        "C1CNP(=O)(OC1)N(CCCl)CCCl",
        "CC(=O)OCC(=O)[C@]1(CC[C@@H]2[C@@]1(CC(=O)[C@H]3[C@H]2CCC4=CC(=O)CC[C@]34C)C)O",
        "CC(=O)OCC(=O)[C@]1(CC[C@@H]2[C@@]1(C[C@@H]([C@H]3[C@H]2CCC4=CC(=O)CC[C@]34C)O)C)O",
        "CC(C(=O)O)O",
        "CC(C)C(C)/C=C/C(C)C1CCC\\2C1(CCC/C2=C/C=C/3\\CC(CCC3=C)O)C",
        "CC(C)C(C)/C=C/C(C)C1CCC\\2C1(CCC/C2=C/C=C\\3/CC(CCC3=C)O)C",
        "CC(C)C(C)/C=C/C(C)C1CCC\\2C1(CCC/C2=C\\C=C/3\\CC(CCC3=C)O)C",
        "CC(C)C(C)/C=C/C(C)C1CCC\\2C1(CCC/C2=C\\C=C\\3/CC(CCC3=C)O)C",
        "CC(C)C(C)C=CC(C)C1CCC2C1(CCCC2=CC=C3CC(CCC3=C)O)C",
        "CC(C)C(C)C=CC(C)C1CCC2[C@@]1(CCCC2=CC=C3CC(CCC3=C)O)C",
        "CC(C)C(C)C=CC(C)C1CC[C@@H]2[C@@]1(CCCC2=CC=C3CC(CCC3=C)O)C",
        "CC1=C(C(=O)C2=C(C1=O)N3C[C@H]4[C@@H]([C@@]3([C@@H]2COC(=O)N)OC)N4)N",
        "CCC1(C(=O)NC(=O)NC1=O)C2=CC=CC=C2",
        "CCCCC1C(=O)N(N(C1=O)C2=CC=CC=C2)C3=CC=CC=C3",
        "CCOC(=O)C1(CCN(CC1)C)C2=CC=CC=C2.Cl",
        "C[C@@H](/C=C/[C@H](C)C(C)C)[C@H]1CC[C@@H]\\2[C@@]1(CCC/C2=C/C=C\\3/C[C@H](CCC3=C)O)C",
        "C[C@@H](/C=C/[C@H](C)C(C)C)[C@H]1CC[C@H]\\2[C@@]1(CCC/C2=C/C=C/3\\C[C@H](CCC3=C)O)C",
        "C[C@@H]1C[C@H]2[C@@H]3CCC4=CC(=O)C=C[C@@]4([C@]3([C@H](C[C@@]2([C@]1(C(=O)CO)O)C)O)F)C",
        "C[C@H](/C=C/[C@@H](C)C(C)C)[C@H]1CC[C@@H]2[C@@]1(CCCC2=C/C=C/3\\C[C@H](CCC3=C)O)C",
        "C[C@H](/C=C/[C@@H](C)C(C)C)[C@H]1CC[C@@H]\\2[C@@]1(CCC/C2=C\\C=C/3\\C[C@H](CCC3=C)O)C",
        "C[C@H](/C=C/[C@H](C)C(C)C)C1CCC\\2[C@@]1(CCC/C2=C\\C=C/3\\C[C@H](CCC3=C)O)C",
        "C[C@H](/C=C/[C@H](C)C(C)C)C1CC[C@@H]\\2[C@@]1(CCC/C2=C\\C=C/3\\C[C@H](CCC3=C)O)C",
        "C[C@H](/C=C/[C@H](C)C(C)C)[C@H]1CCC2[C@@]1(CCCC2=C/C=C/3\\C[C@H](CCC3=C)O)C",
        "C[C@H](/C=C/[C@H](C)C(C)C)[C@H]1CCCC2[C@@]1(CCCC2=CC=C3C[C@H](CCC3=C)O)C",
    ],
    invalid=[
        "HELLOWORLD",
        "ABCDEFG",
    ],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[],
)


def test_smiles_field():
    """Test SMILESField with predefined test cases."""
    field = SMILESField()
    field.test(smiles_test_cases)
