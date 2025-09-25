# 😱 OMGUI

### _Open-source Molecular Graphical User Interface_

<!-- [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/omgui)](https://pypi.org/project/omgui/) -->
<!-- [![PyPI version](https://img.shields.io/pypi/v/omgui)](https://pypi.org/project/omgui/) -->

[![License MIT](https://img.shields.io/github/license/acceleratedscience/openad-toolkit)](https://opensource.org/licenses/MIT)

<!-- [![License MIT](https://img.shields.io/pypi/frameworkversions/jupyterlab/omgui)](https://jupyter.org/) -->

OMGUI makes it dead-simple to visualize and triage your molecule results in Python.  
It supports small molecules as well as macromolecules like proteins, plus it does a [whole lot more](docs/readme.md).

Run it from a **Jupyter Notebook** or any **Python** script.

[![Documentation](docs/assets/btn-docs.svg)](docs/readme.md#omgui---documentation)
[![Quick start](docs/assets/btn-quick-start.svg)](#quick-start)

> [!IMPORTANT]
> OMGUI is in active development. Not all described functionality is implemented yet.  
> A stable version will be released on PyPI in due time.

<br>

### Installation

More details under [Installation](docs/installation.md).

```shell
pip install git+https://github.com/themoenen/omgui.git@v0.1
```

```python
import omgui

omgui.show_mol('dopamine')
```

<br>

## Quick Start

### Inspect a Set of Molecules

```python
import omgui

omgui.show_mols(["C(C(=O)O)N", "C1=CC=CC=C1", "CC(CC(=O)O)O"])
```

<kbd><img src="docs/assets/gui-molset.png" /></kbd>

<br>

### Inspect a Single Molecule

```python
import omgui

omgui.show_mol('dopamine')
```

<kbd><img src="docs/assets/gui-molecule.png" /></kbd>

<br><br>

To discover what else **omgui** can do for you, jump to [Functionality](docs/functionality.md).

<!-- ```shell
yes | plotly_get_cxrome
``` -->

<!-- source ../agenv/bin/activate -->

<!-- python -m test -->
