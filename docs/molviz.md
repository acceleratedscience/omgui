<sub>[&larr; BACK](readme.md)</sub>

# OMGUI - `molviz` - Molecule Visualization

![chartviz sub-module](https://img.shields.io/badge/sub--module-omgui.molviz-yellow)

The `molviz` sub-module lets you visualize molecules on the fly, in 2D and 3D, either as SVG or PNG.

Note that the [chart](chartviz) & molecule visualization requires additional dependencies:

```shell
pip install git+https://github.com/themoenen/omgui.git@v0.1[viz]
```

![Molecule visualization with omgui.molviz](assets/mol-example-quercetin--2d.svg)

<br>

## Instructions

In order to use the molecule visualization, simply start the server in the background, then compose your url:

`/viz/mol/<SMILES>&output=<svg/png>`

```python
import omgui

omgui.launch()
```

```text
http://localhost:8024/viz/mol/C1=CC(=C(C=C1C2=C(C(=O)C3=C(C=C(C=C3O2)O)O)O)O)O?highlight=c1ccccc1&width=800&height=400
```

### Demo Interface

Use the demo interface to see what options are available and how to compose your URL.

http://localhost:8024/viz/mol

![chartviz demo UI](assets/molviz-demo-ui.png)

<br>

## Deployment

Because the chart visualization depends on some system requirements for the PNG/SVG output to work, it's recommended to deploy it using Docker or Podman, as the [Dockerfile](Dockerfile) takes care of installing these dependencies. See `apt-get` and `plotly_get_chrome`.

<br>

## Examples

![Example molecules: argipressin 2D](assets/mol-example-argipressin--2d.svg)
![Example molecules: argipressin 3D](assets/mol-example-argipressin--3d.svg)
![Example molecules: quercetin 2D](assets/mol-example-quercetin--2d.svg)
![Example molecules: quercetin 3D](assets/mol-example-quercetin--3d.svg)
![Example molecules: vitamin B6 2D](assets/mol-example-vitamin-b6--2d.svg)
![Example molecules: vitamin B6 3D](assets/mol-example-vitamin-b6--3d.svg)
