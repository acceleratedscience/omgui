<!-- source ../agenv/bin/activate -->

# OMGUI

**_Open Modular Graphical User Interface_**

OMGUI lets you visualize files, molecules and data.

<br>

## Tl;dr

```
pip install omgui
```

```python
from omgui import molecules

# Display a molecule
molecules.show('dopamine')

# Save & display molecules in your working set
molecules.add('CCO')
molecules.showAll()
```

<br>

### Viewers & File Formats

-   File browser
-   Data viewer (CSV)
-   Molecule viewer (SDF, MOL)
-   Protein viewer (CIF, PDB)
-   PDF viewer (PDF)
-   Text viewer (TXT, default)

<br>

### Direct Visualisation

Generate molecular images and data charts on the fly as PNG of SVG.

-   [Charting API](https://omgui.onrender.com/demo/charts) to turn JSON into charts on the fly:
    -   Bar charts
    -   Line charts
    -   Box Plots
    -   Scatter plot
    -   Histogram
    -   Bubble chart
-   [Molecules API](https://omgui.onrender.com/demo) to visualize SMILES in 2D and 3D

<br>

## Installation

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
pip install -r requirements.txt
```

```shell
yes | plotly_get_chrome
```

```
uvicorn 'app.main:app' --host=0.0.0.0 --port=8034 --reload  --no-access-log
```

<br>

### Deployment

To deploy this app, use the [Dockerfile](Dockerfile), as it installs some system requirements for the Plotly PNG/SVG output to work.
