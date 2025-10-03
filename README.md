![omgui](docs/assets/omgui-header.webp)

# OMGUI

### _Open-source Molecular Graphical User Interface_

<!-- [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/omgui)](https://pypi.org/project/omgui/) -->
<!-- [![PyPI version](https://img.shields.io/pypi/v/omgui)](https://pypi.org/project/omgui/) -->
<!-- ![Static Badge](https://img.shields.io/badge/IBM-Research-0F62FE?style=for-the-badge) -->

[![License MIT](https://img.shields.io/github/license/acceleratedscience/openad-toolkit?style=flat-square)](https://opensource.org/licenses/MIT)

<!-- [![License MIT](https://img.shields.io/pypi/frameworkversions/jupyterlab/omgui)](https://jupyter.org/) -->

OMGUI is a web interface that makes it dead-simple to visualize and triage your molecule results in Python.  
It supports small molecules as well as macromolecules like proteins.

Run it from a **Jupyter Notebook** or any **Python** script.

```python
import omgui
omgui.show_mol('dopamine')
```

Included are also the [chartviz](docs/chartviz.md) and [molviz](docs/molviz.md) sub-libraries for generating charts an molecular images in 2D & 3D.

[![Documentation](docs/assets/btn-docs.svg)](#documentation)
[![Quick start](docs/assets/btn-quick-start.svg)](#quick-start)

![IBM Research](docs/assets/dev-at-ibm-research.svg)

<br><br>

### Installation

More details under [Installation](docs/installation.md).

```shell
pip install git+https://github.com/themoenen/omgui.git@v0.1
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

<br>

## Documentation

1.  [Installation](docs/installation.md)
1.  [Configuration](docs/config.md)
1.  [GUI](docs/gui.md) - Graphical user interface for molecules and data
1.  [molviz](docs/molviz.md) - Sub-module for molecule visualization
1.  [chartviz](docs/chartviz.md) - Sub-module for chart visualisation
1.  [about](docs/about.md)

<br><br><br><br><br><br><br>

## Troubleshooting

<!-- Blocker port -->
<details>
<summary>Shutting down a blocked port</summary>
<br>

> If the OMGUI server didn't shut down properly and is occupying a port, you can shut it down by visiting:
>
> ```
> http://localhost:8024/shutdown
> ```
>
> If this didn't work, you can always run: `kill -9 $(lsof -ti:8024)`

</details>

<!-- Inspect config -->
<details>
<summary>Inspecting config</summary>
<br>

> To get an overview of your current configuration including the source of each value, you can run:
>
> ```python
> from omgui import config
>
> config.report()
> ```
>
> For more, visit [config documentation](docs/config.md)

</details>

<details>
<summary>Inspecting context</summary>
<br>

> To debug your current context (which sets your workspace), you can run:
>
> ```
> import omgui
>
> omgui.get_context()
> ```

</details>
