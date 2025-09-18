from typing import Any
from omgui import ctx


def add(identifier: str, basic: bool = False) -> None:
    """
    Add a molecule to the current workspace's working set.
    """
    from omgui.gui_services import srv_molecules

    enrich = not basic
    srv_molecules.add_mol_to_mws(identifier, enrich=enrich)


def remove(identifier: str) -> None:
    """
    Remove a molecule from the current workspace's working set.
    """
    from omgui.gui_services import srv_molecules

    srv_molecules.remove_mol_from_mws(identifier)


def clear() -> None:
    """
    Clear the current molecule working set.
    """
    from omgui.gui_services import srv_molecules

    srv_molecules.clear_mws()


def get() -> list[dict[str, Any]]:
    """
    Get the current molecule working set.
    """
    return ctx().mws()


def get_names() -> list[str]:
    """
    Get list of molecule names from your working set.
    """
    from omgui.workers.smol_transformers import molset_to_names_list

    mws = ctx().mws()
    return molset_to_names_list(mws)


def count() -> int:
    """
    Get the number of molecules in the current working set.
    """
    return len(ctx().mws())


def is_empty() -> bool:
    """
    Returns whether the current molecule working set is empty.
    """
    return len(ctx().mws()) == 0


def open() -> None:
    """
    Open the current molecule working set in the GUI.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    return _gui_init(path="mws")
