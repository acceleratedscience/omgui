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
- [2. Molecule Viewer](#2-molecule-viewer)
- [3. Molset Viewer](#3-molset-viewer)
- [4. Data Viewer](#4-data-viewer)
- [5. Molecule Working Set](#5-molecule-working-set)
- [6. Results](#6-results)

<br>

## 1. File Browser

<details>
<summary>About</summary>

The file browser lets your browse the files in your workspace. It lets you open molecule files directly into the molecule viewer.

| File type | Suffix       | Type            | Description                                                                                              |
| --------- | ------------ | --------------- | -------------------------------------------------------------------------------------------------------- |
| JSON      | .smol.json   | Small molecules | OMGUI's JSON schema for individual small molecules, can be exported to SDF or CSV                        |
| JSON      | .mmol.json   | Macromolecules  | OMGUI's JSON schema for individual macromolecules, can be exported to CIF or PDB or CSV                  |
| JSON      | .molset.json | Molecule sets   | OMGUI's JSON schema for a set of small molecules. Sets of macromolecules are not supported at this time. |

| File type | Suffix | Type            | Description                                                                                                                                                                         |
| --------- | ------ | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| MDL       | .mol   | Small molecules | Small molecule file holding information about the atoms, bonds, connectivity and coordinates of a molecule - [Wikipedia](https://en.wikipedia.org/wiki/Chemical_table_file#Molfile) |
| SDF       | .sdf   | Molecule sets   | Multi-molecule version of an MDL file - [Wikipedia](https://en.wikipedia.org/wiki/Chemical_table_file#SDF)                                                                          |
| SMI       | .smi   | Molecule sets   | A basic text file with a SMILES string per line                                                                                                                                     |
| CIF       | .cif   | Macromolecules  | Stands for "Crystallographic Information File" and was intended as a successor to the PDB format - [Wikipedia](https://en.wikipedia.org/wiki/Crystallographic_Information_File)     |
| PDB       | .pdb   | Macromolecules  | Stands for "Protein Data Bank" - [Wikipedia](<https://en.wikipedia.org/wiki/Protein_Data_Bank_(file_format)>)                                                                       |
| JSON      | .json  | Data            | Open standard data serialization format [Wikipedia](https://en.wikipedia.org/wiki/JSON)                                                                                             |
| YAML      | .yml   | Data            | Human-readable data serialization format - [Wikepedia](https://simple.wikipedia.org/wiki/YAML)                                                                                      |
| CSV       | .csv   | Data            | Comma-separated text data format - [Wikipedia](https://en.wikipedia.org/wiki/Comma-separated_values)                                                                                |
| TEXT      | .text  | Text            | Basic text format                                                                                                                                                                   |

Files can easily be opened in your default system app, which is the default for any unsupported file formats.

</details>

<details>
<summary>Command</summary>

`launch gui`

</details>

| ![File Browser](readme/file-browser.png) |
| ---------------------------------------- |

<br>

## 2. Molecule Viewer

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

## 3. Molset Viewer

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
