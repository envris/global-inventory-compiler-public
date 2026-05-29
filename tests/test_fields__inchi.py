"""Test cases for InChI field"""

from rdkit import Chem

from gic.fields import FieldTestCases
from gic.fields.inchi import InChIField

rdk_mol1 = Chem.MolFromSmiles("CCCCC1C(=O)N(N(C1=O)C2=CC=CC=C2)C3=CC=CC=C3")
rdk_mol2 = Chem.MolFromSmiles("CCOC(=O)C1(CCN(CC1)C)C2=CC=CC=C2.Cl")

inchi_test_cases = FieldTestCases(
    valid=[
        "InChI=1S/C12H16N4O2/c1-15-10-8(11(17)16(2)12(15)18)13-9(14-10)7-5-3-4-6-7/h7H,3-6H2,1-2H3,(H,13,14)",
        "InChI=1S/C6H11NO4/c1-7-4(6(10)11)2-3-5(8)9/h4,7H,2-3H2,1H3,(H,8,9)(H,10,11)",
        "InChI=1S/C10H18N2O2/c1-4-7(3)6-10(5-2)8(13)11-9(14)12-10/h7H,4-6H2,1-3H3,(H2,11,12,13,14)",
        "InChI=1S/C6H16N2.C2H4O2/c7-5-3-1-2-4-6-8;1-2(3)4/h1-8H2;1H3,(H,3,4)",
        "InChI=1S/C12H20O3/c1-3-4-5-6-9-10(12(14)15-2)7-8-11(9)13/h9-10H,3-8H2,1-2H3",
    ],
    invalid=[
        "InChI=1S/C6H16N2.C2H4O2/c7-5-3-1-2-4-6-8;1-2(3)4/h1-8H2;1H3,(H,3,4",
        "1S/C6H11NO4/c1-7-4(6(10)11)2-3-5(8)9/h4,7H,2-3H2,1H3,(H,8,9)(H,10,11)",
    ],
    valid_formatted=[],
    invalid_formatted=[],
    patched=[],
    generated=[
        (rdk_mol1, Chem.MolToInchi(rdk_mol1)),
        (rdk_mol2, Chem.MolToInchi(rdk_mol2)),
    ],
)


def test_inchi_field():
    """Test InChIField with predefined test cases"""
    field = InChIField()
    field.test(inchi_test_cases)
