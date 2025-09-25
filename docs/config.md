[&larr; back](../)

# OMGUI - Configuration

OMGUI comes with a number of configurable options.  
These can be set in different ways, depending on your preferences or needs.

In order of priority:

1. [Runtime configuration](#1-runtime-configuration) &rarr; `omgui.configure(...)`
1. [Environment variables](#2-environment-variables) &rarr; `OMGUI_*`
1. [Configuration file](#3-configuration-file) &rarr; `omgui.config.yml`
1. Default values

<br>

## Configuration Options

| Option       | Env                | Default   | Advanced | Description                                                                                                                                                                                                                                                                                                                                  |
| :----------- | :----------------- | :-------- | :------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| session      | OMGUI_SESSION      | False     |          | When set to True, your actions are isolated to your sessions. This means that changing your workspace or storing molecules in your working set won't affect other sessions, and your molecule working set will be cleared at the end of the session. This can be useful when working in Jupyter Notebook across multiple workspaces at once. |
| prompt       | OMGUI_PROMPT       | True      |          | Whether to show confirmation prompts for certain actions. If set to False, any possible prompts will be skipped and the default action will be taken. Examples are clearing your molecule working set, or overwriting a file. This may be desired in the context of an API.                                                                  |
| workspace    | OMGUI_WORKSPACE    | DEFAULT   |          | The workspace to be set on startup. If the given workspace doesn't exist, it will be created.                                                                                                                                                                                                                                                |
| data_dir     | OMGUI_DATA_DIR     | ~/.omgui  |    ✓     | The main directory on your file system where your context and your workspaces are stored. When integrating OMGUI into your own application, you may want to set this to a sub-directory of your existing app directory.                                                                                                                      |
| host         | OMGUI_HOST         | localhost |          | The URL host of where the OMGUI server will be launched. If you want to expose it on your network, you will want to set this to `0.0.0.0`.                                                                                                                                                                                                   |
| port         | OMGUI_PORT         | 8024      |          | The URL port where the OMGUI server will be launched. When the default port `8024` is taken, OMGUI will automatically try `8025`, then `8026` etc. However, When a custom port is configured, only that port will be used.                                                                                                                   |
| base_path    | OMGUI_BASE_PATH    | <empty>   |          | The base path for all GUI urls. This is useful when you want to reverse-proxy the service to another domain or port.<br>For example, you may want to expose `http://localhost:8024/~/candidates.sdf` at `https://myapp.com/omgui/~/candidates.sdf`.                                                                                          |
| sample_files | OMGUI_SAMPLE_FILES | True      |          | Set this to False if you don't want to include the sample files in the DEFAULT workspace when created. This may be desired to avoid clutter in your deployment.                                                                                                                                                                              |
| log_level    | OMGUI_LOG_LEVEL    | INFO      |          | Choose what [logging level](https://docs.python.org/3/library/logging.html#logging-levels) is used. Choose from `NOT_SET`, `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`.                                                                                                                                                                |

<br>

## Setting Configuration

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
