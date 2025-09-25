[&larr; back](../)

# OMGUI - Configuration

OMGUI comes with a number of configurable options.  
These can be set in different ways, depending on your preferences or needs.

In order of priority:

1. Runtime configuration (`omgui.configure(...)`)
1. Environment variables (`OMGUI_*`)
1. Configuration file (`omgui.config.yml`)
1. Default values

<br>

### 1. Runtime configuration

Call `omgui.configure(...)` right after import:

```python
import omgui
omgui.configure(session=True, workspace="MY_WORKSPACE")
```

<br>

### 2. Environment variables

Every colnfiguration option has a matching environment variable in SCREAMING_SNAKE_CASE with the "OMGUI\*" prefix.

So for example, `config.session` corresponds to `OMGUI_SESSION`, `config.workspace` to `OMGUI_WORKSPACE`, etc.

<br>

### 3. Configuration file

For permanent preferences, it's recommended to use a `omgui.config.yml` configuration file stored in the root of your application.

```yaml
log_level: ERROR
sample_files: false
```
