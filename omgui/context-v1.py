"""
OMGUI config + context manager
"""

import json
from pathlib import Path

from config import config
from helpers import logger
from openad.helpers.output import output_text, output_error, output_success


class Context:
    """
    Application context manager for OMGUI.
    """

    # Config
    dir: str

    # Context
    workspace: str
    mws: list
    vars: dict

    # Default context values
    default_context = {
        "workspace": "DEFAULT",
        "mws": [],
        "vars": {},
    }

    # ------------------------------------
    # region - Initialization
    # ------------------------------------

    def __init__(self, session_ctx=False):
        """
        Initializes the context manager.

        If session_ctx is True, a new context is created for the session
        without loading from or saving to disk. This is useful for when
        you wish to work separately in parallel contexts (e.g., in Jupyter notebooks).
        """

        # Create the data directory if it doesn't exist
        if not Path(config.get("dir")).exists():
            Path(config.get("dir")).mkdir(parents=True, exist_ok=True)

        # A: Create virgin session context
        if session_ctx:
            _context = self.default_context

        # B: Load global context from file
        else:
            _context = self._load_global_context()

        # Set context attributes
        for key, value in self.default_context.items():
            if key in _context:
                setattr(self, key, _context[key])
            else:
                setattr(self, key, value)

        # Create virgin context: first time / new session
        self._save()

    def _load_global_context(self):
        """
        Loads a saved context file from the data directory.

        Returns:
            dict: The context dictionary, or None if the file is not found.
        """
        try:
            context_path = Path(config.get("dir")) / "context.json"

            # Load from file
            if context_path.exists():
                with open(context_path, "r", encoding="utf-8") as file:
                    context = json.load(file)
                    return context

            # Fall back to deault
            else:
                logger.info("Creating new context file")
                return self.default_context

        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"An error occurred while loading the context file: {e}")
            return self.default_context

    # endregion
    # ------------------------------------
    # region - Core
    # ------------------------------------

    def _save(self):
        """
        Saves the current context to the context file in the data directory.
        """
        try:
            context_path = Path(config.get("dir")) / "context.json"
            with open(context_path, "w", encoding="utf-8") as file:
                json.dump(self.__dict__, file, indent=4)
        except Exception as err:  # pylint: disable=broad-except
            logger.error(f"An error occurred while saving the context file: {err}")

    def display(self):
        """
        Displays the current context, mainly for debugging purposes.
        """
        print("\n\nCurrent OMGUI Context:\n")
        print(json.dumps(self.__dict__, indent=4), "\n")

    # endregion
    # ------------------------------------
    # region - Workspaces
    # ------------------------------------

    def create_workspace(self, workspace_name):
        """
        Creates a new workspace with the specified name if it doesn't already exist.
        """
        # Create the workspace in the context
        workspace_name = workspace_name.strip().replace(" ", "_").upper()
        if workspace_name in self.workspaces():
            logger.warning(f"A workspace named {workspace_name} already exists")
            return
        self.workspace = workspace_name

        # Create the directory
        self._create_workspace_dir(workspace_name)

        self._save()
        # logger.info(f"Created new workspace: {workspace_name}")
        # self.display()
        output_success(f"Created new workspace: <yellow>{workspace_name}</yellow>")

    def set_workspace(self, workspace_name):
        """
        Sets the current workspace to the specified one if it exists.
        """
        # Set the workspace in the context
        workspace_name = workspace_name.strip().replace(" ", "_").upper()
        if workspace_name not in self.workspaces():
            logger.warning(
                f"There is no workspace named '{workspace_name}', creating it"
            )
            return
        self.workspace = workspace_name

        # Create the directory if it doesn't exist
        self._create_workspace_dir(workspace_name, warn=True)

        self._save()
        # logger.info(f"Switched to workspace: {workspace_name}")
        output_success(f"Switched to workspace: <yellow>{workspace_name}</yellow>")

    def _create_workspace_dir(self, workspace_name, warn=False):
        """
        Creates the directory for the specified workspace if it doesn't exist.
        """
        workspace_path = Path(config.get("dir")) / "workspaces" / workspace_name
        if not (workspace_path).exists():
            if warn:
                logger.warning(f"Missing workspace dir '{workspace_name}', creating it")
            workspace_path.mkdir(parents=True, exist_ok=True)

    def workspace_path(self):
        """
        Returns the current workspace path.
        """
        return Path(config.get("dir")) / "workspaces" / self.workspace

    def workspaces(self):
        """
        Returns the list of workspace names.
        """
        workspaces_path = Path(config.get("dir")) / "workspaces"
        if workspaces_path.exists():
            return [p.name for p in workspaces_path.iterdir() if p.is_dir()]
        else:
            return []

    # endregion
    # ------------------------------------


# Global context
ctx = Context()
