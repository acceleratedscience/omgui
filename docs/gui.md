<sub>[&larr; BACK](readme.md)</sub>

# OMGUI - GUI<!-- omit in toc -->

The GUI provides a visual window onto your molecular data, helping you with evaluation and triage.

#### How it works<!-- omit in toc -->

It can be launched from any **Python** script (in the browser) or from a **Jupyter Notebook** (in an iframe).  
Any function that requires the GUI will start the server, which will then keep on running until the application or Notebook is shut down.

If you wish to start the server in the background, you can run:

```
omgui.launch()
```

### Components<!-- omit in toc -->

-   [1. File Browser](#1-file-browser)
    -   [Supported File Formats](#supported-file-formats)
-   [2. Molecule Viewer](#2-molecule-viewer)
-   [3. Molset Viewer](#3-molset-viewer)
-   [4. Data Viewer (coming soon)](#4-data-viewer-coming-soon)
-   [5. Molecule Working Set](#5-molecule-working-set)
    -   [Adding a Property](#adding-a-property)
        -   [How to Format Property Data](#how-to-format-property-data)
    -   [Exporting Your Molecules](#exporting-your-molecules)
-   [6. Results (coming soon)](#6-results-coming-soon)

<br>

## 1. File Browser

The file browser lets your browse the files in your workspace. It lets you open molecule files directly into the molecule viewer.

Files can easily be opened in their default system app, which is also the default for any unsupported file formats.

```python
import omgui

# Show your workspace files in the GUI
omgui.show_files()

# Open a file in the GUI
omgui.open_file('my_candidates/batch_1.sdf')

# Open a file in its default OS application
omgui.open_file_os('my_candidates/batch_1.sdf')
```

<kbd><img src="assets/gui-file-browser.png" alt="GUI File browser"></kbd>

### Supported File Formats

| Filetype   | Suffix            | Content        | Description                                                                                                                                                                          |
| :--------- | :---------------- | :------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| OMGUI_JSON | .smol.json        | Small molecule | OMGUI's JSON schema for individual small molecules, can be exported to SDF or CSV format                                                                                             |
| OMGUI_JSON | .mmol.json        | Macromolecule  | OMGUI's JSON schema for individual macromolecules, can be exported to CIF, PDB or CSV format                                                                                         |
| OMGUI_JSON | .molset.json      | Molecule set   | OMGUI's JSON schema for a set of small molecules.<br>Sets of macromolecules are not supported at this time.                                                                          |
|            |                   |                |                                                                                                                                                                                      |
| MDL        | .mol              | Small molecule | Small molecule file holding information about the atoms, bonds, connectivity and coordinates of a molecule - [learn more](https://en.wikipedia.org/wiki/Chemical_table_file#Molfile) |
| SDF        | .sdf              | Molecule set   | Multi-molecule version of an MDL file - [learn more](https://en.wikipedia.org/wiki/Chemical_table_file#SDF)                                                                          |
| SMI        | .smi              | Molecule set   | A basic text file with a SMILES string per line                                                                                                                                      |
| CIF        | .cif              | Macromolecule  | Stands for "Crystallographic Information File" and is intended as a successor to the PDB format - [learn more](https://en.wikipedia.org/wiki/Crystallographic_Information_File)      |
| PDB        | .pdb              | Macromolecule  | Stands for "Protein Data Bank" and described the three-dimensional structures of molecules - [learn more](<https://en.wikipedia.org/wiki/Protein_Data_Bank_(file_format)>)           |
| JSON       | .json             | Data           | Open standard data serialization format [learn more](https://en.wikipedia.org/wiki/JSON)                                                                                             |
| YAML       | .yml              | Data           | Human-readable data serialization format - [learn more](https://simple.wikipedia.org/wiki/YAML)                                                                                      |
| TEXT       | .text             | Text           | Basic text format                                                                                                                                                                    |
| CSV        | .csv              | Data           | `COMING SOON` Comma-separated text data format - [learn more](https://en.wikipedia.org/wiki/Comma-separated_values)                                                                  |
| PDF        | .pdf              | Rich document  | `COMING SOON` Standard documents including text formatting and images - [learn more](https://en.wikipedia.org/wiki/PDF)                                                              |
| SVG        | .svg              | Vector image   | `COMING SOON` XML-based vector graphics format for defining two-dimensional graphics - [learn more](https://en.wikipedia.org/wiki/SVG)                                               |
| IMG        | .png/jpg/gif/webp | Bitmap image   | `COMING SOON` Various standard web image formats                                                                                                                                     |

<br>

## 2. Molecule Viewer

The molecule viewer gives you an at-a-glance overview of all available information on a particular molecule, as well as a 2D and interactive 3D visualization.

New molecules are by default prepopulated with data from RDKit and (when available) PubChem, while custom properties can be added via the [molecule working set](#5-molecule-working-set).

```python
import omgui

omgui.show_mol("dopamine")
omgui.show_mol("C1=CC(=C(C=C1CCN)O)O") # SMILES
omgui.show_mol("InChI=1S/C8H11NO2/c9-4-3-6-1-2-7(10)8(11)5-6/h1-2,5,10-11H,3-4,9H2") # InChI
omgui.show_mol("VYFYYTLLBUKUHU-UHFFFAOYSA-N") # InChIKey - only when available on PubChem
omgui.show_mol(681) # PubChem CID - only when available on PubChem
omgui.open_file('dopamine.smol.json') # Molecule file formats - only when available on PubChem
```

<kbd><img src="assets/gui-molecule-viewer.png" alt="GUI Molecule viewer"></kbd>

<br>

## 3. Molset Viewer

The molset viewer lets you view, sort and triage a paginated set of molecules.

In the future you can expect more advanced functionality like filtering, subsetting, merging and data visualizations.

```python
import omgui

omgui.show_mols(["C(C(=O)O)N", "C1=CC=CC=C1", "CC(CC(=O)O)O"])
omgui.open_file("neurotransmitters.molset.json")
omgui.open_file("neurotransmitters.sdf")
omgui.open_file("neurotransmitters.smi")
omgui.open_file("neurotransmitters.csv") # Support coming soon
```

<kbd><img src="assets/gui-molset-viewer.png" alt="GUI Molset viewer"></kbd>

<br>

## 4. Data Viewer (coming soon)

> [!IMPORTANT]  
> Not yet implemented, coming soon.

The data viewer will let you easily view an edit data from a CSV or YAML file.  
This includes editing values as well as adding, removing and renaming rows or columns.

<br>

## 5. Molecule Working Set

Your molecules working set (or "MWS") functions as a basket for storing and processing selected candidate molecules.

Each workspace has their own MWS. The MWS lets you easily fetch your molecules as a list of SMILES to be processed by your software, model or function of choice, and then lets you update your molecules with the newly calculated properties.

```python
from omgui import mws

mws.add("C(C(=O)O)N")
mws.add("C1=CC=CC=C1")
mws.add("dopamine")
mws.remove("C1=CC=CC=C1")

mws.add_prop(my_results)

mws.open()
```

<kbd><img src="assets/gui-mws.png" alt="GUI Molset viewer"></kbd>

<br>

### Adding a Property

Once you've calculated a property for your molecules, you can easily update the MWS with your new data.

```python
# Get a list of your molecules as SMILES
my_candidates = mws.get_smiles()

# Do your calculations
results = some_processing_here(my_candidates)

# Update the molecules in your working set
mws.add_prop(results)

# Export your results as SDF file
# Supported file extensions: json, csv, sdf, smi
mws.export("my_candidates.sdf")
```

```python
# Clear your working set to start over
mws.clear()
```

<br>

#### How to Format Property Data

The `add_prop()` function supports result data in various formats. Which format you use is up to you.

1. **Sequential input:**  
   Update all molecules at once, where the length of the input should match the length of the MWS.

    ```python
    # Format A: List of values + property name
    # --> Sequential
    # --> Single property

    results_2 = [0.238, 0.598]
    mws.add_prop(results_2, prop_name="foo_A")
    ```

    ```python
    # Format B: List of dicts
    # --> Sequential
    # --> Multiple properties supported

    results_1 = [
       { "foo_B": 0.729 },
       { "foo_B": 1.235, "bar_B": 0.927 }
    ]
    mws.add_prop(results_1)
    ```

2. **Non-sequential input:**  
   Update select molecules, which are identified by the 'subject' identifier containing the canonical SMILES.

    ```python
    # Format C: List of dicts with subject
    # --> Non-sequential
    # --> Multiple properties supported

    results_3 = [
       { "foo_C": 0.729, "subject": "NCC(=O)O" },
       { "foo_C": 1.235, "bar_C": 0.927, "subject": "CC(O)CC(=O)O" }
    ]
    mws.add_prop(results_3)
    ```

    ```python
    # Format D: Dataframe with subject, prop, val columns
    # --> Non-sequential
    # --> Single property
    # --> Useful when adding property data from CSV

    import pandas as pd
    results_4 = {
       "subject": ["NCC(=O)O", "CC(O)CC(=O)O"],
       "prop": ["foo_D", "foo_D"],
       "val": [0.526, 0.192],
    }
    df = pd.DataFrame(results_4)
    mws.add_prop(df)
    ```

<br>

### Exporting Your Molecules

You can easily fetch your working set molecules in different formats.

```python
from omgui import mws

mws_dicts = mws.get()         # Your molecules as list of dictionaries
mws_smiles = mws.get_smiles() # Your molecules as list of SMILES
mws_names = mws.get_names()   # Your molecules as list of names
count = mws.count()           # Count your molecules
is_empty = mws.is_empty()     # Check if you have any molecules saved
```

And you can just as easily save your working set molecules to disk.

The provided file extension will define the format used to export.
Supported formats are JSON, CSV, SDF and SMI

```python
from omgui import mws

mws.export("my_candidates.json") # JSON file
mws.export("my_candidates.csv")  # CSV file
mws.export("my_candidates.sdf")  # SDF file
mws.export("my_candidates.smi")  # Text file with one SMILES per line
```

Provided paths that start with with `./`, `../`, `~/` or `/` are treated as regular system paths.  
Any other paths are considered workspace paths.

```python
from omgui import mws

# Workspace paths
mws.export("my_candidates.csv")                          # Workspace path
mws.export(".my_candidates.csv")                         # Workspace path
mws.export("foo/my_candidates.csv")                      # Workspace path

# System paths
mws.export("./my_candidates.csv")                        # Your current working directory
mws.export("../my_candidates.csv")                       # Your current working directory's parent
mws.export("~/my_candidates.csv")                        # Your user directory
mws.export("/Users/johndoe/Downloads/my_candidates.csv") # Absolute path
```

<br>

## 6. Results (coming soon)

> [!IMPORTANT]  
> Not yet implemented, coming soon.

Your results page will hold a history of result sets that were saved.

```python
import omgui.results

results.add(["C(C(=O)O)N", "C1=CC=CC=C1"]) # To be inmplemented
results.open() # To be inmplemented
```
