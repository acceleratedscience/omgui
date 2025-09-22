# OMGUI

## _Open Modular Graphical User Interface_

OMGUI is a dead-simple python module to visualize and triage your molecule results.

It supports small molecules as well as macromolecules like proteins, plus it does a [whole lot more](#quick-start).

Run it from a Jupyter Notebook or any python script:

```python
import omgui

omgui.show_molset(["C(C(=O)O)N", "C1=CC=CC=C1", "CC(CC(=O)O)O"])
```

<!-- ![molecule](docs/assets/gui-molset.png) -->

<kbd><img src="docs/assets/gui-molset.png" /></kbd>

```python
omgui.show_mol('dopamine')
```

![molecule](docs/assets/gui-molecule.png)

> [!WARNING]  
> OMGUI is in development. Not all described functionality is implemented yet.

<br>

### Installation

> [!NOTE]  
> _Optional: create virtual environment_
>
> ```shell
> python -m venv .venv
> ```
>
> ```shell
> source .venv/bin/activate
> ```

```shell
# pip install omgui # To be published
pip install git+https://github.com/themoenen/omgui@gui_merge
```

<!-- ```shell
yes | plotly_get_cxrome
``` -->

<br>

## Quick Start

### Molecule viewer

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

<!-- source ../agenv/bin/activate -->

<!-- python -m test -->
