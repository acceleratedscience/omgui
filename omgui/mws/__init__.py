from typing import Any
from omgui import context


def add(identifier: str, basic: bool = False) -> None:
    """
    Add a molecule to the current workspace's working set.
    """
    from omgui.gui_services.molecules import GUIMoleculesService

    ctx = context.get()
    molecules_srv = GUIMoleculesService(ctx)
    enrich = not basic
    molecules_srv.add_mol_to_mws(identifier, enrich=enrich)


def remove(identifier: str) -> None:
    """
    Remove a molecule from the current workspace's working set.
    """
    from omgui.gui_services.molecules import GUIMoleculesService

    ctx = context.get()
    molecules_srv = GUIMoleculesService(ctx)
    molecules_srv.remove_mol_from_mws(identifier)


def clear() -> None:
    """
    Clear the current molecule working set.
    """
    from omgui.gui_services.molecules import GUIMoleculesService

    ctx = context.get()
    molecules_srv = GUIMoleculesService(ctx)
    molecules_srv.clear_mws()


def get() -> list[dict[str, Any]]:
    """
    Get the current molecule working set.
    """

    ctx = context.get()
    return ctx.mws()


def get_names() -> list[str]:
    """
    Get list of molecule names from your working set.
    """
    from omgui.workers.smol_transformers import molset_to_names_list

    ctx = context.get()
    mws = ctx.mws()
    return molset_to_names_list(mws)


def open() -> None:
    """
    Open the current molecule working set in the GUI.
    """
    from omgui.gui_launcher import gui_init as _gui_init

    ctx = context.get()
    return _gui_init(ctx, path="mws")
