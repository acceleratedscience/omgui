<sub>[home](../#readme) / [docs](readme.md) / about</sub>

# OMGUI - About

This project was developed by [@themoenen](https://github.com/themoenen) for [IBM Research](https://research.ibm.com) as part of the [OpenAD Toolkit](https://openad.accelerate.science/) under the [Accelerated Discovery](https://accelerate.science) project.

### Contributions

OMGUI is fully open-source and [pull requests](../pulls) are welcome.  
For suggestions & bug reports you can always create an [issues](../../../issues).

### The Stack

-   The OMGUI server lives in this repository and is written in Python.
-   The OMGUI frontend lives in the [omgui-frontend](https://github.com/acceleratedscience/omgui-frontend) repo.  
    It is written in Vue.js, using the composition API with TypeScript enabled.
-   The [chartviz] and [molviz] modules rely on basic template rendering with [Jinja](https://jinja.palletsprojects.com).
-   Molecule rendering uses [RDKit](https://github.com/rdkit/rdkit#readme) for 2D rendering and [cinemol](https://github.com/moltools/CineMol#readme) for 3D molecules.

[chartviz]: chartviz.md
[molviz]: molviz.md
