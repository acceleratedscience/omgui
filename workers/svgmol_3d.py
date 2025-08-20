import re
import time
import logging
from enum import Enum
from rdkit import Chem
from random import randint
from rdkit.Chem import AllChem
from typing import Optional, Literal, List
from cinemol.api import Atom, Bond, Look, Style, draw_molecule

logger = logging.getLogger(__name__)


def render(
    # fmt: off
    smiles: str,
    width: Optional[int] = 600,
    height: Optional[int] = 450,
    highlight: Optional[str] = None,
    # 3D specific options
    style: Literal['SPACEFILLING', 'BALL_AND_STICK', 'TUBE', 'WIREFRAME'] = 'BALL_AND_STICK',
    look: Literal['CARTOON', 'GLOSSY'] = 'CARTOON',
    rot_random: bool = True,
    rot_x: Optional[float] = None,
    rot_y: Optional[float] = None,
    rot_z: Optional[float] = None,
    # fmt: on
) -> str:
    """
    Render 3D molecule from SMILES string to SVG format.

    Args:
        smiles (str): The SMILES string of the molecule
        width (int): Width of the rendered image in pixels
        height (int): Height of the rendered image in pixels
        substructure (str): Optional SMARTS substructure to highlight in the molecule

    Returns:
        str: 3D SVG representation of the molecule
    """

    # Create RDKit molecule
    mol = Chem.MolFromSmiles(smiles)  # pylint: disable=E1101

    # Get coordinates for 3D rendering
    conformer = _get_conformer(mol)
    pos = conformer.GetPositions()

    # Parse atoms and bonds from molecule
    atoms, bonds = [], []

    # Set substructure colors
    atom_colors = {}

    # Highlight substructure if provided
    if highlight:
        for atom_index in find_substructure(mol, highlight):
            atom_colors[atom_index] = (230, 25, 75)

    color = _random_pastel_color()
    for atom in mol.GetAtoms():
        # if atom.GetSymbol() == "H":
        #     continue
        color = atom_colors.get(atom.GetIdx(), color)
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

    # Set rotation angles
    rot_x = rot_x if rot_x != None else randint(0, 600) / 100 if rot_random else 0
    rot_y = rot_y if rot_y != None else randint(0, 600) / 100 if rot_random else 0
    rot_z = rot_z if rot_z != None else randint(0, 600) / 100 if rot_random else 0

    # Draw molecule.
    svg = draw_molecule(
        atoms=atoms,
        bonds=bonds,
        style=_parse_style(style),
        look=_parse_look(look),
        resolution=50,
        # Not obvious: rotation is in increments of 60°, so 6 = 360°
        rotation_over_y_axis=rot_x,
        rotation_over_x_axis=rot_y,
        rotation_over_z_axis=rot_z,
        # view_box=(0, -0, 2000, 2000),  # (x, y, width, height)
        scale=50,
    )

    # Success
    svg_str = svg.to_svg()

    # Add width & height
    regex_pattern = r'(<svg[^>]*?viewBox="[^"]*?")'
    replacement_string = rf'\1 width="{width}" height="{height}">'
    svg_str = re.sub(regex_pattern, replacement_string, svg_str)

    # Report
    svg_size = len(svg.to_svg()) / 1000
    logger.info(f"Runtime: {1000 * (time.time() - t0)} ms")
    logger.info(f"File size: {svg_size} kb")

    return svg_str


def _get_conformer(mol: Chem.Mol) -> Chem.Conformer:
    """
    Generate the molecule's conformer.
    """

    # Prepare the molecule for 3D rendering
    mol = Chem.AddHs(mol)  # pylint: disable=E1101
    # AllChem.EmbedMolecule(mol)  # pylint: disable=E1101
    AllChem.EmbedMolecule(
        mol, useRandomCoords=True, randomSeed=0xF00D
    )  # pylint: disable=E1101
    AllChem.MMFFOptimizeMolecule(mol)  # pylint: disable=E1101

    # Generate conformer
    return mol.GetConformer()


def _random_pastel_color() -> tuple[int, int, int]:
    """
    Generate a random pastel color.
    """
    r = randint(200, 215)
    g = randint(200, 215)
    b = randint(200, 215)
    return (r, g, b)


def _parse_style(style_string: str) -> Style:
    """
    Convert string style parameter to Style enum
    """
    try:
        return Style[style_string]
    except KeyError:
        return Style.BALL_AND_STICK


def _parse_look(look_string: str) -> Look:
    """
    Convert string look parameter to Look enum
    """
    try:
        return Look[look_string]
    except KeyError:
        return Look.CARTOON


def find_substructure(mol: Chem.Mol, smarts: str) -> List[int]:
    """
    Find a substructure in a molecule.

    :param Chem.Mol mol: Molecule to find a substructure in.
    :param str smarts: SMARTS string to use for substructure search.
    :return: List of atom indices that match the substructure.
    :rtype: ty.List[int]
    """
    substructure = Chem.MolFromSmarts(smarts)
    matches = mol.GetSubstructMatches(substructure)
    return [atom_index for match in matches for atom_index in match]
