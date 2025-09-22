[&larr; back](../)

# OMGUI - Functionality <!-- omit in toc -->

<!--  ### Table of Contents omit in toc -->

- [Molecule viewer](#molecule-viewer)
- [Data Viewer](#data-viewer)
- [Molecule 2D/3D Visualizer](#molecule-2d3d-visualizer)

<br>

## Molecule viewer

Inspect a single molecule:

```python
omgui.show_mol('dopamine')
```

> Supports `SMILES` and `InChI` identifiers, and if the molecule exists on PubChem, you can also find it by `name`, `InChIKey` or PubChem `CID`.

Inspect a set of molecules:

```python
omgui.show_molset(["C(C(=O)O)N", "C1=CC=CC=C1", "CC(CC(=O)O)O"])
```

> Supported identifiers are `SMILES` and `InChI`.

<br>

## Data Viewer

The data viewer lets you easily view an edit data from a CSV file. This includes editing values as well as adding, removing and renaming rows or columns.

> [!WARNING]  
> Not yet implemented, coming soon.

<br>

## Molecule 2D/3D Visualizer

The visualizer library lets you generate `SVG` or `PNG` images on the fly for any molecule, including optional substructure highlighting.
