[&larr; back](../)

# OMGUI - Functionality <!-- omit in toc -->

<!--  ### Table of Contents omit in toc -->

- [Molecule viewer](#molecule-viewer)
- [Data Viewer](#data-viewer)
- [Molecule 2D/3D Visualizer](#molecule-2d3d-visualizer)
- [Chart Visualizer](#chart-visualizer)

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

> [!WARNING]  
> Not yet implemented, coming soon.

```python
from omgui import molviz

molviz.2d('CCO')
```

```python
molviz.3d('CCO')
```

<br>

## Chart Visualizer

The chart visualizer lets you generate various types of charts on the fly.  
Supported charts are:

-   bar charts
-   line charts
-   pie charts
-   scatter plots
-   bubble charts
-   box plots
-   histograms

```python
from omgui import chartviz

groups = ["Group A", "Group B", "Group C"]
data = [
    {
        "keys": groups,
        "name": "Flamingo",
        "data": [ 56, 79, 10 ]
    },
    {
        "keys": groups,
        "name": "Possum",
        "data": [ 81, 10, 50 ]
    },
    {
        "keys": groups,
        "name": "Shrew",
        "data": [ 99, 20, 45 ]
    }
]

chartviz.boxplot(data)
```

<!-- <br>

## Utils

OMGUI comes with a number of utility functions that may come in handy.

```python
from omgui.util.workers import smol_transformers

smol_transformers
``` -->
