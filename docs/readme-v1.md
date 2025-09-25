<sub>[&larr; BACK](../)</sub>

# OMGUI - Documentation<!-- omit in toc -->

### Table of Contents<!-- omit in toc -->

- [Molecule viewer](#molecule-viewer)
- [Molecule Working Set](#molecule-working-set)
- [Data Viewer](#data-viewer)
- [Molecule 2D/3D Visualizer](#molecule-2d3d-visualizer)
- [Chart Visualizer](#chart-visualizer)

The OpenAD GUI provides a visual window onto your data, helping you with evaluation and triage.

The code base for the GUI lives in a separate (not yet public) repository:<br>
[https://github.com/acceleratedscience/openad-gui]()

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

## Molecule Working Set

Your molecules working set (or "mws") functions as a basket where you can store selected candidates for further processing.

> [!WARNING]  
> Partly implemented.

```python
from omgui import mws

# Add some molecules and inspect them in the GUI
mws.add("C(C(=O)O)N")
mws.add("C1=CC=CC=C1")
mws.open()
```

```python

# Get a list of your molecules as SMILES
my_candidates = mws.get_smiles()

# Perform any type of property calculation
my_calculated_prop_result = [
    { "foo": 0.729 },
    { "foo": 1.235 }
]

# Update the molecules in your working set
mws.add_props(my_calculated_prop_result)

# Export your results as SDF file
mws.export(format="sdf")
```

```python
# Clear your working set to start over
mws.clear()
```

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

> [!WARNING]  
> Not yet implemented, coming soon.

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
