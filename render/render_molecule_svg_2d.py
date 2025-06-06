from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D


def render_molecule_svg_2d(
    smiles: str,
    width: int = 600,
    height: int = 450,
    highlight: str = None,
) -> str:
    """
    Render a 2D molecule from SMILES string to SVG format.

    Args:
        smiles (str): The SMILES string of the molecule (InChI also accepted)
        highlight (str, optional): A SMARTS pattern to highlight specific substructures

    Returns:
        str: SVG representation of the molecule
    """
    try:
        if not smiles:
            raise ValueError("Please provide inchi_or_smiles.")

        # Generate RDKit molecule object.
        mol_rdkit = Chem.MolFromInchi(smiles)
        if not mol_rdkit:
            mol_rdkit = Chem.MolFromSmiles(smiles)  # pylint: disable=no-member

        if highlight:
            substructure = Chem.MolFromSmarts(highlight)  # pylint: disable=no-member
            matches = mol_rdkit.GetSubstructMatches(substructure)

            # Flatten the tuple of tuples into a list of atom indices
            highlight_atoms = [atom_index for match in matches for atom_index in match]
        else:
            highlight_atoms = None

        mol_drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        mol_drawer.DrawMolecule(mol_rdkit, highlightAtoms=highlight_atoms)
        mol_drawer.FinishDrawing()
        return mol_drawer.GetDrawingText()

    except Exception as e:
        print(f"Error generating SVG: {e}")
        return None
