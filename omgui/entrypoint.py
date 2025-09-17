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

# import atexit
import urllib
from typing import Any
from pathlib import Path
from . import context

from openad.helpers.output import output_text, output_error, output_success

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
    ctx = context.get()
    ctx_dict = ctx.get()
    return ctx_dict


def launch(*args: Any, **kwargs: Any) -> Any:
    """
    Launch the GUI server.
    """
    from .gui_launcher import gui_init as _gui_init

    ctx = context.get()
    return _gui_init(ctx, *args, **kwargs)


def shutdown(*args: Any, **kwargs: Any) -> Any:
    """
    Shutdown the GUI server.
    """
    from .gui_launcher import gui_shutdown as _gui_shutdown

    ctx = context.get()
    return _gui_shutdown(ctx, *args, **kwargs)


# endregion
# ------------------------------------
# region - Molecules
# ------------------------------------


def show_mol(molecule_identifier: str = "") -> None:
    """
    Open the molecule viewer for a given molecule identifier.
    """
    from .gui_launcher import gui_init as _gui_init

    ctx = context.get()
    path = "mol/" + urllib.parse.quote(molecule_identifier, safe="/")
    _gui_init(ctx, path)


def show_molset(path: str = "") -> None:
    """
    Open the molecule set viewer for a given molecule set path.
    """
    from .gui_launcher import gui_init as _gui_init

    if Path(path).suffix == "":
        path += ".molset.json"

    ctx = context.get()
    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(ctx, path)


# endregion
# ------------------------------------
# region - Molecule Working Set
# ------------------------------------


class MWS:

    def add(self, identifier: str, basic: bool = False) -> None:
        """
        Add a molecule to the current workspace's working set.
        """
        from gui_services.molecules import GUIMoleculesService

        ctx = context.get()
        molecules_srv = GUIMoleculesService(ctx)
        enrich = not basic
        molecules_srv.add_mol_to_mws(identifier, enrich=enrich)

    def remove(self, identifier: str) -> None:
        """
        Remove a molecule from the current workspace's working set.
        """
        from gui_services.molecules import GUIMoleculesService

        ctx = context.get()
        molecules_srv = GUIMoleculesService(ctx)
        molecules_srv.remove_mol_from_mws(identifier)

    def clear(self) -> None:
        """
        Clear the current molecule working set.
        """
        from gui_services.molecules import GUIMoleculesService

        ctx = context.get()
        molecules_srv = GUIMoleculesService(ctx)
        molecules_srv.clear_mws()

    def get(self) -> list[dict[str, Any]]:
        """
        Get the current molecule working set.
        """

        ctx = context.get()
        return ctx.mws()

    def get_names(self) -> list[str]:
        """
        Get list of molecule names from your working set.
        """
        from workers.smol_transformers import molset_to_names_list

        ctx = context.get()
        mws = ctx.mws()
        return molset_to_names_list(mws)

    def open(self) -> None:
        """
        Open the current molecule working set in the GUI.
        """
        from .gui_launcher import gui_init as _gui_init

        ctx = context.get()
        return _gui_init(ctx, path="mws")


mws = MWS()

# endregion
# ------------------------------------
# region - Workspaces
# ------------------------------------


def get_workspace() -> str:
    """
    Get the current workspace.
    """

    ctx = context.get()
    return ctx.workspace


def get_workspaces() -> list[str]:
    """
    Get  the list of available workspaces.
    """

    ctx = context.get()
    return ctx.workspaces()


def set_workspace(name: str) -> bool:
    """
    Set the current workspace.
    """

    ctx = context.get()
    return ctx.set_workspace(name)


def create_workspace(name: str) -> bool:
    """
    Create a new workspace.
    """

    ctx = context.get()
    return ctx.create_workspace(name)


# endregion
# ------------------------------------
# region - Files
# ------------------------------------


def show_files(*args: Any, **kwargs: Any) -> Any:
    """
    Open the file browser.
    """
    from .gui_launcher import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def show_file(path: str = "") -> Any:
    """
    Open the appropriate viewer for a given file path.
    """
    from .gui_launcher import gui_init as _gui_init

    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(path)


# endregion
# ------------------------------------


# atexit.register()
