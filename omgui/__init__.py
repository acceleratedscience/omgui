# pylint: disable=import-outside-toplevel

"""
Public methods for the omgui library.
Served via __init__.py.

Usage:
    import omgui
    omgui.launch()
    omgui.shutdown()
    etc.
"""


import urllib
from typing import Any
from pathlib import Path
from omgui import context

from openad.helpers.output import output_text, output_error, output_success

# Sub-modules
from omgui import mws

# Load context
ctx = context.get()

# ------------------------------------
# region - General
# ------------------------------------


def session(workspace: str = "DEFAULT") -> Any:
    """
    Set the context to a session-only context,
    with optional focus on the given workspace.
    """

    context.set_session(workspace)
    output_success(
        [
            f"✅ Session-only context created - workspace: {workspace}",
            "Your molecule working set will reset when you exit this session.",
        ],
        return_val=False,
    )


def get_context():
    """
    Get the current context.

    Returns:
        dict: The context dictionary.
    """
    ctx_dict = ctx.get()
    return ctx_dict


def launch(*args: Any, **kwargs: Any) -> Any:
    """
    Launch the GUI server.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    return _gui_init(ctx, *args, **kwargs)


def shutdown(*args: Any, **kwargs: Any) -> Any:
    """
    Shutdown the GUI server.
    """
    from omgui.gui_launcher import gui_shutdown as _gui_shutdown

    return _gui_shutdown(ctx, *args, **kwargs)


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
    _gui_init(ctx, path)


def show_molset(path: str = "") -> None:
    """
    Open the molecule set viewer for a given molecule set path.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    if Path(path).suffix == "":
        path += ".molset.json"

    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(ctx, path)


# endregion
# ------------------------------------
# region - Workspaces
# ------------------------------------


def get_workspace() -> str:
    """
    Get the current workspace.
    """
    return ctx.workspace


def get_workspaces() -> list[str]:
    """
    Get  the list of available workspaces.
    """
    return ctx.workspaces()


def set_workspace(name: str) -> bool:
    """
    Set the current workspace.
    """
    return ctx.set_workspace(name)


def create_workspace(name: str) -> bool:
    """
    Create a new workspace.
    """
    return ctx.create_workspace(name)


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
