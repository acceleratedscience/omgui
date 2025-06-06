# Molecular Visualisation

Demo visualisation API to experiment with agentic workflows.

See it in actions:
[molvis.onrender.com/demo](https://molvis.onrender.com/demo)

It uses [RDKit](https://www.rdkit.org/) to generate the conformers and to render 2D SVGs, and [Cinemol](https://github.com/moltools/CineMol) to render 3D SVGs.

### Launch

```
uvicorn 'main:app' --host=0.0.0.0 --port=8034 --reload
```

### Infer

Optional parameters

|               |        |                |                                                           |
| ------------- | ------ | -------------- | --------------------------------------------------------- |
| width         | number | None           | Width of the image                                        |
| height        | number | None           | Height of the image                                       |
| png           | bool   | 0              | Render PNG instead of SVG                                 |
| highlight     | str    | None           | SMARTS substructure to highlight                          |
| d3            | bool   | 0              | Render the molecule in 3D                                 |
| d3_rot_x      | number | None           | 3D rotation around the X axis in 60° units                |
| d3_rot_y      | number | None           | 3D rotation around the Y axis in 60° units                |
| d3_rot_z      | number | None           | 3D rotation around the Z axis in 60° units                |
| d3_rot_random | bool   | 0              | Random 3D rotation if not specified                       |
| d3_style      | str    | BALL_AND_STICK | `BALL_AND_STICK` / `SPACE_FILLING` / `TUBE` / `WIREFRAME` |
| d3_look       | str    | CARTOON        | `CARTOON` / `GLOSSY`                                      |

**2D**

-   http://localhost:8034/render-molecule-svg?smiles=Clc1cc(Cl)c(Cl)c(-c2c(Cl)c(Cl)cc(Cl)c2Cl)c1Cl
-   http://localhost:8034/render-molecule-svg?smiles=CC(C)Oc1cc(-n2nc(C(C)(C)C)oc2=O)c(Cl)cc1Cl

![image](assets/hematein-2d.svg)
![image](assets/oxadiazon-2d.svg)

**3D**

-   http://localhost:8034/render-molecule-svg?smiles=Clc1cc(Cl)c(Cl)c(-c2c(Cl)c(Cl)cc(Cl)c2Cl)c1Cl&d3=1
-   http://localhost:8034/render-molecule-svg?smiles=CC(C)Oc1cc(-n2nc(C(C)(C)C)oc2=O)c(Cl)cc1Cl&d3=1

![image](assets/hematein-3d.svg)
![image](assets/oxadiazon-3d.svg)

<!-- source ../agenv/bin/activate -->
