"""
Configuration options for the omgui library.

Configuration settings order of priority:
    1. Programatically via omgui.configure()
    2. Environment variables (OMGUI_*)
    3. Configuration file (omgui.config.yml)
    4. Default values

Usage:
    from omgui import config

    if config.prompt:
        ...
"""

# Std
import os
from pathlib import Path

# 3rd party
import yaml

# OMGUI
from omgui.spf import spf
from omgui.util.logger import get_logger


logger = get_logger()


def config():
    """
    Get the config singleton instance.
    """
    return Config()


class Config:
    """
    Configuration singleton for omgui.

    Every option corresponds to an environment variable
    in SCREAMING_SNAKE_CASE.

    Priorities (high to low):
        1. omgui.configure() during runtime
        2. Environment variables (OMGUI_*)
        3. Configuration file (omgui.config.yml)
        4. Default values

    Options
    -------
    session: bool, default False / .env: OMGUI_SESSION
        By default, all omgui instances share a global context,
        with a persistent molecule working set per workspace.
        When you switch workspace, this affects all sessions.
        When you set session=True, a new session-only context
        is created, which does not affect other sessions. Your
        molecule working set will reset when you exit this session.

    prompt: bool, default True / .env: OMGUI_PROMPT
        Whether to show confirmation prompts for certain actions.
        If set to False, all prompts will be skipped and the
        default action will be taken.

    workspace: str, default "DEFAULT" / .env: OMGUI_WORKSPACE
        Set workspace on startup. If the given workspace doesn't
        exist, it will be created.

    data_dir: str, default "~/.omgui" / .env: OMGUI_DATA_DIR
        Data directory for the application storage.

    host: str, default "localhost" / .env: OMGUI_HOST
        Hostname for the GUI server. Use "0.0.0.0" to
        allow external access.

    port: int, default 8024 / .env: OMGUI_PORT
        Port for the GUI server. If occupied, the next
        available port will be used, so 8025 etc.

    base_path: str, default "" / .env: OMGUI_BASE_PATH
        Base path for the GUI server. If you are running
        the server behind a reverse proxy, you might need
        to set this to the subpath where the server is reachable.
        For example, if the server is reachable at
        "https://mydomain.com/omgui/", set base_path to "/omgui".

    sample_files: bool, default True / .env: OMGUI_SAMPLE_FILES
        Whether to add file samples to DEFAULT workspace on first run.

    log_level: str, default "INFO" / .env: OMGUI_LOG_LEVEL
        Log level for the server. One of "DEBUG", "INFO",
        "WARNING", "ERROR", "CRITICAL".
    """

    # Singleton instance
    _instance = None
    _initialized = False

    # Config options from file / env
    _config_file = None
    _config_env = None

    # Default config
    default_config = {
        "session": False,
        "prompt": True,
        "workspace": "DEFAULT",
        "data_dir": "~/.omgui",
        "host": "localhost",
        "port": 8024,
        "base_path": "",
        "sample_files": True,
        "log_level": "INFO",
    }

    # Config settings set via omgui.configure() during runtime
    config_runtime = {}

    def __new__(cls):
        """
        Control singleton instance creation.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the configuration by loading from environment variables,
        configuration file, and setting defaults.
        """
        # Prevent re-initialization of singleton
        if self._initialized:
            return

        _config = (
            self.default_config  # Base: defaults
            | self.config_file()  # 3nd priority: omgui.config.yml
            | self.config_env()  # 2nd priority: environment variables
            | self.config_runtime  # 1st priority: set via omgui.configure()
        )

        # Write to self
        for key, value in _config.items():
            if self.default_config.get(key) is not None:
                setattr(self, key, value)

        # Create the data directory if it doesn't exist
        if not Path(_config.get("data_dir")).expanduser().exists():
            logger.info(
                "Creating missing omgui data directory at '%s'", _config.get("data_dir")
            )
            Path(_config.get("data_dir")).expanduser().mkdir(
                parents=True, exist_ok=True
            )

    def config_file(self):
        """
        Returns the loaded config file as a dict.
        """
        if self._config_file is None:
            self._config_file = self._load_config_file()
        return self._config_file

    def _load_config_file(self):
        """
        Loads configuration from a YAML file.
        Returns a dict.
        """

        _config_file = {}
        try:
            config_path = Path(os.getcwd()) / "omgui.config.yml"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as file:
                    _config_file = yaml.safe_load(file)
                    _config_file = _config_file if _config_file else {}

            # Log what's loaded
            _file_vars = list(_config_file.keys())
            logger.info(
                "Loaded config options from file omgui.config.yml: %s",
                ", ".join(_file_vars) if _file_vars else "None",
            )

            return _config_file

        except Exception as err:  # pylint: disable=broad-except
            logger.error("An error occurred while loading the config file: %s", err)
            return {}

    def config_env(self):
        """
        Returns the loaded config env as a dict.
        """
        if self._config_env is None:
            self._config_env = self._load_config_env()
        return self._config_env

    def _load_config_env(self):
        """
        Loads configuration from environment variables.
        Returns a dict.
        """
        _config_env = {}
        for key, val in self.default_config.items():
            env_var = f"OMGUI_{key.upper()}"
            if env_var in os.environ:
                val = os.environ[env_var]
                if isinstance(val, bool):
                    val = val.lower() in ("true", "1", "yes")
                elif isinstance(val, int):
                    val = int(val)
                _config_env[key] = val

        # Log what's loaded
        _env_vars = list(_config_env.keys())
        logger.info(
            "Loaded config options from environment variables: %s",
            ", ".join(_env_vars) if _env_vars else "None",
        )
        return _config_env

    def set(self, key, value):
        """
        Set a configuration value.
        This is used by omgui.config(key=val)
        """

        if key in self.default_config:
            self.config_runtime[key] = value
            logger.info("Config '%s' set to '%s'", key, value)
        else:
            logger.warning("Config key '%s' not recognized.", key)

    def report(self):
        """
        Prints an overview of the current configuration.
        """
        _report = []
        _report.append("<h1>Compiled config</h1>")
        for key, val in self.__dict__.items():
            if not key.startswith("_"):
                _report.append(f"<green>{key:12}</green><soft>:</soft> {val}")

        spf("\n".join(_report), pad=2, edge=True)
        _report = []

        _report.append("<h2>Configuration Sources:</h2>\n")

        _report.append("  1. Config runtime")
        for key, val in self.config_runtime.items():
            _report.append(f"     {key:12}: {val}")
        if len(self.config_runtime.items()) == 0:
            _report.append("     <soft>None</soft>")

        _report.append("\n  2. Config env")
        for key, val in self.config_env().items():
            _report.append(f"     {key:12}: {val}")
        if len(self.config_env().items()) == 0:
            _report.append("     <soft>None</soft>")

        _report.append("\n  3. Config file")
        for key, val in self.config_file().items():
            _report.append(f"     {key:12}: {val}")
        if len(self.config_file().items()) == 0:
            _report.append("     <soft>None</soft>")

        _report.append("\n  4. Default config:")
        for key, val in self.default_config.items():
            _report.append(f"     {key:12}: {val}")

        spf("\n".join(_report), pad_btm=2)
