import re
import time
from random import randint
from rdkit import Chem
from rdkit.Chem import AllChem

from cinemol.api import Atom, Bond, Look, Style, draw_molecule


def render_molecule_svg_3d(smiles: str) -> str:
    """
    Render 3D molecule from SMILES string to SVG format.

    Args:
        smiles (str): The SMILES string of the molecule

    Returns:
        str: SVG representation of the molecule
    """
    mol = Chem.MolFromSmiles(smiles)
    # Generate conformer
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=0xF00D)
    AllChem.MMFFOptimizeMolecule(mol)
    pos = mol.GetConformer().GetPositions()

    # Parse atoms and bonds from molecule.
    atoms, bonds = [], []

    for atom in mol.GetAtoms():
        if atom.GetSymbol() == "H":
            continue
        color = (220, 220, 200)
        atoms.append(
            Atom(atom.GetIdx(), atom.GetSymbol(), pos[atom.GetIdx()], color=color)
        )

    for bond in mol.GetBonds():
        if (
            bond.GetBeginAtom().GetSymbol() == "H"
            or bond.GetEndAtom().GetSymbol() == "H"
        ):
            continue
        start_index, end_index = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        bonds.append(Bond(start_index, end_index, int(bond.GetBondTypeAsDouble())))

    t0 = time.time()

    # Draw molecule.
    svg = draw_molecule(
        atoms=atoms,
        bonds=bonds,
        style=Style.BALL_AND_STICK,
        look=Look.CARTOON,
        resolution=50,
        # Not obvious: 6 = 360°
        rotation_over_y_axis=randint(0, 600) / 100,
        rotation_over_x_axis=randint(0, 600) / 100,
        rotation_over_z_axis=randint(0, 600) / 100,
        # view_box=(0, -0, 2000, 2000),  # (x, y, width, height)
        scale=50,
    )

    # Success
    svg_str = svg.to_svg()

    # Add width & height
    regex_pattern = r'(<svg[^>]*?viewBox="[^"]*?")'
    replacement_string = r'\1 width="400" height="300">'
    svg_str = re.sub(regex_pattern, replacement_string, svg_str)

    # Report
    svg_size = len(svg.to_svg()) / 1000
    print(f"Runtime: {1000 * (time.time() - t0)} ms")
    print(f"File size: {svg_size} kb")

    return svg_str
