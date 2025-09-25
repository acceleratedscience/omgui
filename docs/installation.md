<sub>[&larr; BACK](readme.md)</sub>

# OMGUI - Installation

> [!TIP]  
> _**Recommended:** create a virtual environment_
>
> ```shell
> python -m venv .venv
> ```
>
> ```shell
> source .venv/bin/activate
> ```

### Basic Install

```shell
pip install git+https://github.com/themoenen/omgui.git@v0.1
```

### Full Install

This installs additional dependencies that are required for the [molviz](molviz.md) and [chartviz](chartviz.md) sub-modules to work.

```shell
pip install git+https://github.com/themoenen/omgui.git@v0.1[viz]
```
