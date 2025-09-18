"""
Public methods for the omgui library.

Sub modules:
    - mws: Molecule working set

Usage:
    import omgui

    omgui.launch()
    omgui.shutdown()

    omgui.mws.add("CCO")
    etc.
"""

# Std
import urllib
from typing import Any
from pathlib import Path

# OMGUI
from omgui import context
from omgui.helpers import logger
from omgui.configuration import config

# Expose for simpler imports in our own codebase
from omgui.context import ctx

# Sub-modules for the public API
from omgui import mws


# ------------------------------------
# region - General
# ------------------------------------


def configure(
    session: bool | None = None,
    prompt: bool | None = None,
    workspace: str | None = None,
    data_dir: str | None = None,
    host: str | None = None,
    port: int | None = None,
    base_path: str | None = None,
    log_level: str | None = None,
) -> None:
    """
    Configuration options to be set right after import.

    See configuration.py for details.
    """

    if session:
        config().set("session", True)
        context.new_session()  # Create a new session-only context

    if prompt:
        config().set("prompt", prompt)

    if workspace:
        config().set("workspace", workspace)
        ctx().set_workspace(workspace)  # Set the workspace in the context

    if data_dir:
        config().set("data_dir", data_dir)

    if host:
        config().set("host", host)

    if port:
        config().set("port", port)

    if base_path:
        config().set("base_path", base_path)

    if log_level:
        config().set("log_level", log_level)
        logger.setLevel(log_level)


def get_context():
    """
    Get the current context.

    Returns:
        dict: The context dictionary.
    """
    ctx_dict = ctx().get_dict()
    return ctx_dict


def launch(*args: Any, **kwargs: Any) -> Any:
    """
    Launch the GUI server.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def shutdown(*args: Any, **kwargs: Any) -> Any:
    """
    Shutdown the GUI server.
    """
    from omgui.gui_launcher import gui_shutdown as _gui_shutdown

    return _gui_shutdown(*args, **kwargs)


# endregion
# ------------------------------------
# region - Molecules
# ------------------------------------


def show_mol(molecule_identifier: str = "") -> None:
    """
    Open the molecule viewer for a given molecule identifier.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    path = "mol/" + urllib.parse.quote(molecule_identifier, safe="/")
    _gui_init(path)


def show_molset(path: str = "") -> None:
    """
    Open the molecule set viewer for a given molecule set path.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    if Path(path).suffix == "":
        path += ".molset.json"

    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(path)


# endregion
# ------------------------------------
# region - Workspaces
# ------------------------------------


def get_workspace() -> str:
    """
    Get the current workspace.
    """
    return ctx().workspace


def get_workspaces() -> list[str]:
    """
    Get  the list of available workspaces.
    """
    return ctx().workspaces()


def set_workspace(name: str) -> bool:
    """
    Set the current workspace.
    """
    return ctx().set_workspace(name)


def create_workspace(name: str) -> bool:
    """
    Create a new workspace.
    """
    return ctx().create_workspace(name)


# endregion
# ------------------------------------
# region - Files
# ------------------------------------


def show_files(*args: Any, **kwargs: Any) -> Any:
    """
    Open the file browser.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def show_file(path: str = "") -> Any:
    """
    Open the appropriate viewer for a given file path.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(path)


# endregion
# ------------------------------------
