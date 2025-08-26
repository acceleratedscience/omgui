<!-- source ../agenv/bin/activate -->

# Data Visualization

Application to visualize data on the fly.  
See it in action: [molvis.onrender.com/demo/charts](https://molvis.onrender.com/demo/charts)

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
