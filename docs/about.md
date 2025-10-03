<sub>[home](../#readme) / [docs](readme.md) / about</sub>

# OMGUI - About

This project was developed by [@themoenen](https://github.com/themoenen) for [IBM Research](https://research.ibm.com) as part of the [OpenAD Toolkit](https://openad.accelerate.science/) under the [Accelerated Discovery](https://accelerate.science) project.

### Contributions

OMGUI is fully open-source and [pull requests](../../../pulls) are welcome.  
For suggestions & bug reports you can always create an [issues](../../../issues).

### The Stack

-   **OMGUI Server**  
    Lives in this repository and is written in Python.

-   **OMGUI Frontend**  
    Lives in the [omgui-frontend] repo. It is written in [Vue.js], using the composition API with [TypeScript] and [SCSS].  
    The molecule viewer relies on [RDKit] for 2D visualization and [Miew] for rendering interactive 3D molecules.

-   **molviz**  
    Uses [RDKit] for 2D rendering and [CineMol] for static 3D molecules.  
    Relies on [Jinja] for basic template rendering.

-   **chartviz**
    Uses [Plotly] as charting engine, which itself relies on [D3].  
    Relies on [Jinja] for basic template rendering.

-   **OMGUI Banner**  
    In case you wondered, the [rotating Icosahedron banner](assets/omgui-header.webp) was created with [Three.js] and then exported to an animated webp image with [FFmpeg]. You can find the repo for that at [omgui-gh-banner]

[chartviz]: chartviz.md
[molviz]: molviz.md
[Vue.js]: https://vuejs.org/
[TypeScript]: https://www.typescriptlang.org
[SCSS]: https://sass-lang.com
[RDKit]: https://github.com/rdkit/rdkit#readme
[Miew]: https://github.com/epam/miew#readme
[Jinja]: https://jinja.palletsprojects.com
[CineMol]: https://github.com/moltools/CineMol#readme
[omgui-frontend]: https://github.com/acceleratedscience/omgui-frontend
[Plotly]: https://plotly.com/python
[D3]: https://d3js.org
[Three.js]: https://threejs.org
[FFmpeg]: https://www.ffmpeg.org
[omgui-gh-banner]: http://github.com/themoenen/omgui-gh-banner
