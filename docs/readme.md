<sub>[&larr; BACK](../)</sub>

# OMGUI - Documentation<!-- omit in toc -->

### Table of Contents<!-- omit in toc -->

- [GUI / Graphical User Interface](#gui--graphical-user-interface)
  - [How it works](#how-it-works)
  - [Components](#components)
  - [1. File Browser](#1-file-browser)
  - [2. Molecule Viewer](#2-molecule-viewer)
  - [3. Molset Viewer](#3-molset-viewer)
  - [4. Data Viewer](#4-data-viewer)
  - [5. "My Molecules" Working Set](#5-my-molecules-working-set)
  - [6. Results](#6-results)
- [Molecule viewer](#molecule-viewer)
- [Molecule Working Set](#molecule-working-set)
- [Data Viewer](#data-viewer)
- [Molecule 2D/3D Visualizer](#molecule-2d3d-visualizer)
- [Chart Visualizer](#chart-visualizer)

The OpenAD GUI provides a visual window onto your data, helping you with evaluation and triage.

The code base for the GUI lives in a separate (not yet public) repository:<br>
[https://github.com/acceleratedscience/openad-gui]()

<br>

## GUI / Graphical User Interface

### How it works

The GUI can be launched from any Python script (in the browser) or a Jupyter Notebook (in an iFrame).  
Any function that requires the GUI will start the GUI server, which will then keep on running until the application or Notebook is shut down.

<br>

### Components

1. File browser
1. Molecule viewer
1. Molecule set viewer
1. Data viewer (to be implemented)
1. "My molecules" working set
1. Results

<br>

### 1. File Browser

<details>
<summary>About</summary>

The file browser lets us open our own proprietary file formats:

-   **.smol.json** --> Individual molecule files
-   **.molset.json** --> Sets of molecule files

As well as a number of commonly used file formats:

-   **.mol**
-   **.sdf**
-   **.smi**
-   **.json**
-   **.csv**

Files can easily be opened in your default system app, which is the default for any unsupported file formats.

</details>

<details>
<summary>Command</summary>

`launch gui`

</details>

| ![File Browser](readme/file-browser.png) |
| ---------------------------------------- |

<br>

### 2. Molecule Viewer

<details>
<summary>About</summary>

The molecule viewer gives you an at-a-glance overview of all the information you have gathered on a particular molecule.

New molecules are prepopulated with data from RDKit and PubChem by default

</details>

<details>
<summary>Command</summary>

`show molecule|mol <name> | <smiles> | <inchi> | <inchikey> | <cid>`

Example: `show mol dopamine`

</details>

| ![Molecule Viewer](readme/molecule-viewer.png) |
| ---------------------------------------------- |

<br>

<br>

### 3. Molset Viewer

<details>
<summary>About</summary>

<p>The molset viewer is replacing the widely used "mols2grid" package. It runs a lot faster and has improved usability.</p>

<p>In the future we'll also load this with more advanced functionality like filtering, subsetting, merging etc.</p>

<p><span style="color: #d00">Note: viewing molecule sets from a dataframe is not yet implemented.</span></p>

</details>

<details>
<summary>Command</summary>

`show molset|molecule set '<molset_or_sdf_or_smi_path>' | using dataframe <dataframe>`

Example: `show molset 'my_mols.molset.json'`

</details>

| ![Molset Viewer](readme/molset-viewer.png) |
| ------------------------------------------ |

<br>

### 4. Data Viewer

<details>
<summary>About</summary>

The data viewer lets you review, sort and triage data from a CSV file or a dataframe.

<span style="color: #d00">The data viewer is not yet ported into the new GUI. It still uses the deprecated Flask app architecture.</span>

</details>

<details>
<summary>Command</summary>

`display data '<filename.csv>'` + `result open`

Example: `display data 'demo/my-data.csv'` + `result open`

</details>

| ![Data Viewer](readme/data-viewer.png) |
| -------------------------------------- |

<br>

### 5. "My Molecules" Working Set

<details>
<summary>About</summary>

Your working set of molecules(\*) is a molset that lives in memory and is meant as a bucket for gathering candidates from various processesses and sources, before storing them into a new file and processing them further.

\(\*) Currently the working set is called "mymols", but this name may change.

<span style="color: #d00">Note: loading and merging molecule sets is still using a different architecture which is not compatible with the GUI.</span>

</details>

<details>
<summary>About</summary>

`show mols`

</details>

| ![My Molecules](readme/my-mols.png) |
| ----------------------------------- |

<br>

### 6. Results

<details>
<summary>About</summary>

Whenever data is displayed in the CLI or a Notebook using `output_table()`, the data is stored in memory so it can be used for follow up commands like `result open`, `result edit`, `result copy` etc.

The result dataset stored in memory can also be viewed and manipulated in the GUI, either through the molecule viewer or the data viewer (yet to be implemented).

</details>

<details>
<summary>About</summary>

`display data '<molecule_data.csv>'` + `result open`

Example: `display data 'demo/my-mols.csv'` + `result open`

</details>

![Results](readme/results.png)

---

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
