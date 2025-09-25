[&larr; back](../)

# OMGUI - Configuration

OMGUI comes with a number of configurable options.  
These can be set in different ways, depending on your preferences or needs.

In order of priority:

1. Runtime configuration (`omgui.configure(...)`)
1. Environment variables (`OMGUI_*`)
1. Configuration file (`omgui.config.yml`)
1. Default values

| Option  | Env var       | Default value | Description                                                                                                                                                                                                                                                                                                                                  |
| ------- | ------------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| session | OMGUI_SESSION | False         | By default, all omgui instances share a global context, with a persistent molecule working set per workspace. When you switch workspace, this affects all sessions. When you set session=True, a new session-only context is created, which does not affect other sessions. Your molecule working set will reset when you exit this session. |

| prompt | OMGUI_PROMPT | True | |
| workspace | OMGUI_WORKSPACE | DEFAULT | |
| data_dir | OMGUI_DATA_DIR | ~/.omgui | |
| host | OMGUI_HOST | localhost | |
| port | OMGUI_PORT | 8024 | |
| base_path | OMGUI_BASE_PATH | <empty> | |
| sample_files | OMGUI_SAMPLE_FILES | True | |
| log_level | OMGUI_LOG_LEVEL | INFO | |
| viz_deps | n/a | False | |

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
