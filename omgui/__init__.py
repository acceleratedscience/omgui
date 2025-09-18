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
from omgui.context import ctx, new_session
from omgui import mws  # Expose sub-modules


from openad.helpers.output import output_text, output_error, output_success


# ------------------------------------
# region - General
# ------------------------------------


def config(
    session: bool = False,
    prompt: bool = True,
    workspace: str = "DEFAULT",
    dir: str = "~/.omgui",
    host: str = "localhost",
    port: int = 8024,
    base_path: str = "",
    log_level: str = "INFO",
) -> None:
    """
    Configuration options to be set right after import.

    Every option corresponds to an environment variable
    in SCREAMING_SNAKE_CASE.

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

    dir: str, default "~/.omgui" / .env: OMGUI_DIR
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

    log_level: str, default "INFO" / .env: OMGUI_LOG_LEVEL
        Log level for the server. One of "DEBUG", "INFO",
        "WARNING", "ERROR", "CRITICAL".
    """

    if session:
        new_session()

    if workspace:
        ctx().set_workspace(workspace)

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
