import os
import yaml
from pathlib import Path
from omgui.helpers import logger


def load_config():
    """
    Loads the omgui.config.yml file from the root of the app,
    or falls back to default config.

    Returns:
        dict: The configuration dictionary.

    Priority:
        ENV var > config file > default
    """
    # Default config
    _config = {
        "dir": "~/.omgui",
    }

    try:
        # Path to the current working directory (the app's root)
        app_root = Path(os.getcwd())
        config_path = app_root / "omgui.config.yml"

        # Check if the config file exists
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as file:
                _config = yaml.safe_load(file)

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"An error occurred while loading the config file: {e}")

    # Prioritize environment variables if set
    _config["dir"] = os.path.expanduser(os.environ.get("OMGUI_DIR", _config.get("dir")))

    # Create the data directory if it doesn't exist
    if not Path(_config["dir"]).exists():
        logger.info(f"Creating omg directory at '{_config['dir']}'")
        Path(_config["dir"]).mkdir(parents=True, exist_ok=True)

    return _config


config = load_config()
