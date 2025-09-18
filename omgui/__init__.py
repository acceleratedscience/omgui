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

# Expose sub-modules for the public API
from omgui import mws

from omgui.context import ctx
from omgui.configuration import get_config

config = get_config()

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
        from omgui import context

        get_config().set("session", True)
        context.new_session()  # Create a new session-only context

    if prompt:
        get_config().set("prompt", prompt)

    if workspace:
        get_config().set("workspace", workspace)
        ctx().set_workspace(workspace)  # Set the workspace in the context

    if data_dir:
        get_config().set("data_dir", data_dir)

    if host:
        get_config().set("host", host)

    if port:
        get_config().set("port", port)

    if base_path:
        get_config().set("base_path", base_path)

    if log_level:
        from omgui.helpers import logger
        from omgui.helpers.jupyter import nb_mode

        get_config().set("log_level", log_level)
        if not nb_mode():
            logger.setLevel(log_level)

    # Update the global config
    global config
    config = get_config()


def get_context() -> dict:
    """
    Get the current context as a dictionary.
    """
    ctx_dict = ctx().get_dict()
    return ctx_dict


def launch(*args, **kwargs) -> None:
    """
    Launch the GUI server.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def shutdown(*args, **kwargs) -> None:
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
    import urllib
    from omgui.gui_launcher import gui_init as _gui_init

    path = "mol/" + urllib.parse.quote(molecule_identifier, safe="/")
    _gui_init(path)


def show_molset(path: str = "") -> None:
    """
    Open the molecule set viewer for a given molecule set path.
    """
    import urllib
    from pathlib import Path
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


def show_files(*args, **kwargs) -> None:
    """
    Open the file browser.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    return _gui_init(*args, **kwargs)


def show_file(path: str = "") -> None:
    """
    Open the appropriate viewer for a given file path.
    """
    import urllib
    from omgui.gui_launcher import gui_init as _gui_init

    path = "~/" + urllib.parse.quote(path, safe="/")
    _gui_init(path)


# endregion
# ------------------------------------
