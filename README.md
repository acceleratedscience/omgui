<!-- source ../agenv/bin/activate -->

# Data Visualization

Application to visualize data on the fly.

-   [Charting API](https://molvis.onrender.com/demo/charts) to turn JSON into charts on the fly
-   [Molecules API](https://molvis.onrender.com/demo) to visualize SMILES in 2D and 3D

<br>

### Install

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
