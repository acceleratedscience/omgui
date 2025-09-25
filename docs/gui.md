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

- [1. File Browser](#1-file-browser)
  - [Supported File Formats](#supported-file-formats)
- [2. Molecule Viewer](#2-molecule-viewer)
- [3. Molset Viewer](#3-molset-viewer)
- [4. Data Viewer](#4-data-viewer)
- [5. Molecule Working Set](#5-molecule-working-set)
- [6. Results](#6-results)

<br>

## 1. File Browser

The file browser lets your browse the files in your workspace. It lets you open molecule files directly into the molecule viewer.

Files can easily be opened in their default system app, which is also the default for any unsupported file formats.

```python
import omgui

omgui.show_files()
omgui.open_file('my_candidates/batch_1.sdf')
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
| CSV        | .csv              | Data           | Comma-separated text data format - [learn more](https://en.wikipedia.org/wiki/Comma-separated_values)                                                                                |
| TEXT       | .text             | Text           | Basic text format                                                                                                                                                                    |
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
omgui.show_mol("VYFYYTLLBUKUHU-UHFFFAOYSA-N") # InChIKey
omgui.show_mol(681) # PubChem CID
omgui.open_file('dopamine.smol.json') # Molecule file formats
```

<kbd><img src="assets/gui-molecule-viewer.png" alt="GUI Molecule viewer"></kbd>

<br>

## 3. Molset Viewer

The molset viewer lets you view, sort and triage a paginated set of molecules.

In the future you can expect more advanced functionality like filtering, subsetting, merging and data visualizations.

<kbd><img src="assets/gui-molset-viewer.png" alt="GUI Molset viewer"></kbd>

<br>

## 4. Data Viewer

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

## 5. Molecule Working Set

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

## 6. Results

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
