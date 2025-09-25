<sub>[&larr; BACK](../#readme)</sub>

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

| Option       | Env                | Default   | Advanced | Description                                                                                                                                                                                                                                                                                                                                                          |
| :----------- | :----------------- | :-------- | :------: | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Title        | OMGUI_TITLE        | omgui     |          | The title displayed in the bottom left-hand corner of the GUI.<br>Note: not visible in Jupyter Notebook.                                                                                                                                                                                                                                                             |
| host         | OMGUI_HOST         | localhost |          | The URL host of where the OMGUI server will be launched. If you want to expose it on your network, you will want to set this to `0.0.0.0`.                                                                                                                                                                                                                           |
| port         | OMGUI_PORT         | 8024      |          | The URL port where the OMGUI server will be launched. When the default port `8024` is taken, OMGUI will automatically try `8025`, then `8026` etc. However, When a custom port is configured, only that port will be used.                                                                                                                                           |
| session      | OMGUI_SESSION      | False     |          | When set to True, your actions are isolated to your sessions. This means that changing your workspace or storing molecules in your working set won't affect other sessions, and your molecule working set will be cleared at the end of the session. This can be useful when working in Jupyter Notebook across multiple workspaces at once.                         |
| workspace    | OMGUI_WORKSPACE    | DEFAULT   |          | The workspace to be set on startup. If the given workspace doesn't exist, it will be created.                                                                                                                                                                                                                                                                        |
| log_level    | OMGUI_LOG_LEVEL    | INFO      |          | Choose what [logging level](https://docs.python.org/3/library/logging.html#logging-levels) is used. Choose from `NOT_SET`, `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`.                                                                                                                                                                                        |
| stateless    | OMGUI_STATELESS    | False     |          | When set to True, OMGUI will behave as a fully stateless application, which means it will visualize anything passed into the URL, but stateful functionality like your filebrowser, molecule working set, molset edit options etc. will be disabled. This can be useful when you want to host OMGUI as a lightweight visualizer shared by different users.           |
| base_path    | OMGUI_BASE_PATH    | <empty>   |    ✓     | Base path for the GUI server. If you are running the server behind a reverse proxy, you will need to set `config.base_path` to where the GUI server is hosted. For example, if the GUI is proxied to "https://mydomain.com/omgui/", you should set the base path to "omgui/". We have a [sample reverse proxy server](../omgui/dev/proxy_server.py) to try this out. |
| redis_url    | OMGUI_REDIS_URL    | None      |    ✓     | Currently this is only used by the [chartviz](chartviz.md) sub-module. When rendering large charts via POST request, the data is stored in memory and an ID is returned. However if you need to deploy your application on a clustered server, this will fall short. All you need is to provide a Redis url and OMGUI will take care of the rest.                    |
| data_dir     | OMGUI_DATA_DIR     | ~/.omgui  |    ✓     | The main directory on your file system where your context and your workspaces are stored. When integrating OMGUI into your own application, you may want to set this to a sub-directory of your existing app directory.                                                                                                                                              |
| prompt       | OMGUI_PROMPT       | True      |    ✓     | Whether to show confirmation prompts for certain actions. If set to False, any possible prompts will be skipped and the default action will be taken. Examples are clearing your molecule working set, or overwriting a file. This may be desired in the context of an API.                                                                                          |
| sample_files | OMGUI_SAMPLE_FILES | True      |    ✓     | Set this to False if you don't want to include the sample files in the DEFAULT workspace when created. This may be desired to avoid clutter in your deployment.                                                                                                                                                                                                      |

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

Every colnfiguration option has a matching environment variable in SCREAMING_SNAKE_CASE with the "OMGUI\_" prefix.

So for example, `config.session` corresponds to `OMGUI_SESSION`, `config.workspace` to `OMGUI_WORKSPACE`, etc.

<br>

### 3. Configuration file

For permanent preferences, it's recommended to use a `omgui.config.yml` configuration file stored in the root of your application.

```yaml
log_level: ERROR
sample_files: false
```
