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


class Context:
    """
    Application context manager for OMGUI.
    """

    # Context
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

    def __init__(self, workspace=None):
        """
        Initializes the context manager.

        If workspace is provided, a new isolated session context is created
        for that workspace which stays in memory and won't save to disk.
        This is useful for when you wish to work separately in parallel contexts
        (e.g., in Jupyter notebooks).
        """

        # A: Create virgin session context
        if workspace:
            _context = self.default_context.copy()
            _context["workspace"] = workspace
            _context["temp"] = True  # Mark as session-only

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
        self._mws = self._load_mws()

        # Create virgin context: first time / workspace session
        self._create_workspace_dir(self.workspace)
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
        # Session context is not saved to disk
        if self.temp:
            return

        try:
            context_path = Path(config.get("dir")) / "context.json"
            with open(context_path, "w", encoding="utf-8") as file:
                print("SAVE:", context_path, self.__dict__)
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

        mws_path = self.workspace_path() / "._system" / "mws.json"

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

    def mws_add(self, smol, silent=False):
        from workers.smol_functions import get_smol_name, get_smol_from_mws

        try:
            name = get_smol_name(smol)
            inchikey = smol.get("identifiers", {}).get("inchikey")

            # Already in mws -> skip
            if get_smol_from_mws(self, inchikey) is not None:
                output_success(
                    f"Molecule <yellow>{name}</yellow> already in working set",
                    return_val=False,
                )
                return True

            # Add to mws
            self._mws.append(smol.copy())
            print(999, self._mws)
            self._save()  # <<

            # Feedback
            if not silent:
                output_success(
                    f"Molecule <yellow>{name}</yellow> was added", return_val=False
                )
            return True

        except Exception as err:  # pylint: disable=broad-except
            if not silent:
                output_error(
                    [f"Molecule <yellow>{name}</yellow> failed to be added", err],
                    return_val=False,
                )
            return False

    def mws_remove(self, smol, silent=False):
        from workers.smol_functions import get_smol_name, get_best_available_identifier

        name = get_smol_name(smol)
        inchikey = smol.get("identifiers", {}).get("inchikey")

        try:
            # Find matching molecule
            for i, item in enumerate(self._mws):
                if item.get("identifiers", {}).get("inchikey") == inchikey:

                    # Remove from mws
                    self._mws.pop(i)
                    self._save()

                    # Feedback
                    if not silent:
                        output_success(
                            f"Molecule <yellow>{name}</yellow> was removed",
                            return_val=False,
                        )
                    return True

            # Not found
            if not silent:
                output_error(
                    f"Molecule <yellow>{name}</yellow> not found in working set",
                    return_val=False,
                )
            return False

        except Exception as err:  # pylint: disable=broad-except
            if not silent:
                output_error(
                    [f"Molecule <yellow>{name}</yellow> failed to be removed", err],
                    return_val=False,
                )
            return False

    # endregion
    # ------------------------------------


# Global context
# ctx = Context()

CURRENT_CONTEXT = Context()


def get():
    """
    Get the current context (global or session).
    """
    return CURRENT_CONTEXT


def set_session(workspace: str):
    """
    Set the current context (global or session).
    """
    global CURRENT_CONTEXT
    CURRENT_CONTEXT = Context(workspace)
