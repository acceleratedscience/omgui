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
from omgui.startup import startup as _startup
from omgui.configuration import config as _config

config = _config()
_startup()

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
    Optional config options to be set right after import.

    This will update config with the provided values.
    See configuration.py for details.
    """

    if session:
        from omgui import context

        _config().set("session", True)
        context.new_session()  # Create a new session-only context

    if prompt:
        _config().set("prompt", prompt)

    if workspace:
        # Workspace gets created in startup()
        _config().set("workspace", workspace)

    if data_dir:
        _config().set("data_dir", data_dir)

    if host:
        _config().set("host", host)

    if port:
        _config().set("port", port)

    if base_path:
        _config().set("base_path", base_path)

    if log_level:
        from omgui.util.jupyter import nb_mode
        from omgui.util.logger import get_logger

        _config().set("log_level", log_level)
        if not nb_mode():
            logger = get_logger()
            logger.setLevel(log_level)

    # Update the global config
    global config
    config = _config()


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


def show_molset(smiles: list[str] = []) -> None:
    """
    Open the molecule set viewer for a list of SMILES.
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
