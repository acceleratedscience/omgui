"""
OMGUI context manager

By default, a global context file is loaded on startup,
which means that if you switch workspaces, this will
affect all sessions of OMGUI.

The user can set the scope to a session-context, which means
that changes to your session context (e.g., switching workspaces)
will not affect the global context or other sessions.
This allows you to work across different workspaces in parallel.

For now, the context is only used to store your current workspace.
Working set molecules are stored per workspace.

Usage:

    import omgui

    # Optional: set session context
    omgui.set_scope('my_workspace')
"""

import json
from pathlib import Path

from config import config
from helpers import logger
from openad.helpers.output import output_text, output_error, output_success


def get():
    """
    Get the context singleton instance.
    """
    return Context()


def set_session(workspace: str):
    """
    Set the current context (global or session).
    """
    Context(session=True, workspace=workspace)


class Context:
    """
    Application context manager for OMGUI.
    """

    # Singleton instance
    _instance = None
    _initialized = False

    # Context values
    workspace: str
    temp: bool = False  # Session-only context
    _mws: list
    vars: dict

    # Default context values
    default_context = {
        "workspace": "DEFAULT",
        "temp": False,
        "vars": {},
        "_mws": [],
    }

    # ------------------------------------
    # region - Initialization
    # ------------------------------------

    def __new__(cls, *args, session: bool = None, workspace: str = None, **kwargs):
        """
        Control singleton instance creation.
        """

        if cls._instance is None or session is True:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, session: bool = None, workspace: str = None):
        """
        Initializes the context manager.

        If workspace is provided, a new isolated session context is created
        for that workspace which stays in memory and won't save to disk.
        This is useful for when you wish to work separately in parallel contexts
        (e.g., in Jupyter notebooks).
        """

        # Prevent re-initialization of singleton
        if self._initialized:
            return

        # A: Create virgin session context
        if session:
            _context = self.default_context.copy()
            _context["workspace"] = workspace
            _context["temp"] = True  # Mark as session-only
            _context["_mws"] = []

        # B: Load global context from file
        else:
            _context = self._load_global_context()

        # Set context attributes
        for key, value in self.default_context.items():
            if key in _context:
                setattr(self, key, _context[key])
            else:
                setattr(self, key, value)

        # Load molecule working set for current workspace into memory
        if not session:
            self._mws = self._load_mws()

        # Create virgin context: first time / workspace session
        self._create_workspace_dir(self.workspace)
        self._save()
        self._initialized = True

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
        # Session context is not saved to disk
        if self.temp:
            return

        try:
            # Save molecule working set
            mws_path = self.mws_path()
            with open(mws_path, "w", encoding="utf-8") as file:
                json.dump(self._mws, file, indent=4)

            # Save context file, without _mws
            ctx_dict = self.__dict__.copy()
            if "_mws" in ctx_dict:
                del ctx_dict["_mws"]
            context_path = Path(config.get("dir")) / "context.json"
            with open(context_path, "w", encoding="utf-8") as file:
                # print("Save ctx:", context_path, _ctx)
                json.dump(ctx_dict, file, indent=4)

        except Exception as err:  # pylint: disable=broad-except
            logger.error(f"An error occurred while saving the context file: {err}")

    def get(self):
        """
        Displays the current context, mainly for debugging purposes.
        """
        ctx_dict = self.__dict__.copy()

        # Replace _mws with summary
        if "_mws" in ctx_dict:
            count = len(ctx_dict["_mws"])
            if count == 0:
                ctx_dict["_mws"] = "<empty>"
            elif count == 1:
                ctx_dict["_mws"] = "<1 molecule>"
            else:
                ctx_dict["_mws"] = f"<{count} molecules>"

        return ctx_dict

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
            self.set_workspace(workspace_name)
            return
        self.workspace = workspace_name

        # Create the directory
        self._create_workspace_dir(workspace_name)

        self._save()
        # logger.info(f"Created new workspace: {workspace_name}")
        # self.display()
        output_success(
            f"Switched to new workspace: <yellow>{workspace_name}</yellow>",
            return_val=False,
        )

    def set_workspace(self, workspace_name):
        """
        Sets the current workspace to the specified one if it exists.
        """
        # Set the workspace in the context
        workspace_name = workspace_name.strip().replace(" ", "_").upper()
        if workspace_name not in self.workspaces():
            logger.error(f"There is no workspace named '{workspace_name}'")
            return
        self.workspace = workspace_name

        self._save()
        # logger.info(f"Switched to workspace: {workspace_name}")
        output_success(
            f"Switched to workspace: <yellow>{workspace_name}</yellow>",
            return_val=False,
        )

    def _create_workspace_dir(self, workspace_name):
        """
        Creates the directory for the specified workspace if it doesn't exist.
        """
        workspace_path = self.workspace_path(workspace_name)
        if not (workspace_path).exists():
            try:
                workspace_path.mkdir(parents=True, exist_ok=True)
                output_success(
                    f"Created new workspace: <yellow>{workspace_path}</yellow>",
                    return_val=False,
                )
            except Exception as err:  # pylint: disable=broad-except
                logger.error(
                    f"An error occurred while creating the '{workspace_name}' workspace directory: {err}"
                )

    def workspace_path(self, workspace=None):
        """
        Returns the current workspace path.
        """

        return Path(config.get("dir")) / "workspaces" / (workspace or self.workspace)

    def mws_path(self, workspace=None):
        """
        Returns the current molecule working set path.
        """

        return self.workspace_path(workspace) / "._system" / "mws.json"

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
    # region - Molecule Working Set
    # ------------------------------------

    def _load_mws(self):
        """
        Loads the molecule working set for the current workspace into memory.
        """

        mws_path = self.mws_path()

        # Read molecules from file
        if mws_path.exists():
            try:
                with open(mws_path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except Exception as err:  # pylint: disable=broad-except
                logger.error(
                    f"An error occurred while loading the molecule working sets: {err}"
                )
                return []

        # Create file if missing
        else:
            mws_path.parent.mkdir(parents=True, exist_ok=True)
            with open(mws_path, "w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
            return []

    def mws(self):
        """
        Returns the current molecule working set.
        """
        if not hasattr(self, "_mws") or self._mws is None:
            self._mws = self._load_mws()
        return self._mws

    def set_mws(self, molset: list):
        """
        Sets the current molecule working set.
        """
        self._mws = molset
        self._save()
        return True

    def mws_add(self, smol):
        """
        Adds a molecule to the current molecule working set.
        """
        self._mws.append(smol.copy())
        self._save()

    def mws_remove(self, i):
        """
        Removes a molecule from the current molecule working set.
        """
        self._mws.pop(i)
        self._save()

    # endregion
    # ------------------------------------
