# Std
from typing import Any

# 3rd party
import pandas as pd

# OMGUI
from omgui.context import ctx


# ------------------------------------
# region - Core
# ------------------------------------


def open() -> None:
    """
    Open the current molecule working set in the GUI.
    """
    from omgui.main import gui_init as _gui_init

    return _gui_init(path="mws")


# endregion
# ------------------------------------
# region - Manipulation
# ------------------------------------


def add(identifier: str, basic: bool = False) -> None:
    """
    Add a molecule to the current workspace's working set.
    """
    from omgui.gui.gui_services import srv_mws

    enrich = not basic
    srv_mws.add_mol_to_mws(identifier, enrich=enrich)


def remove(identifier: str) -> None:
    """
    Remove a molecule from the current workspace's working set.
    """
    from omgui.gui.gui_services import srv_mws

    srv_mws.remove_mol_from_mws(identifier)


def add_prop(prop_list_or_df: list[str] | pd.DataFrame, prop_name: str = None) -> None:
    """
    Add properties to molecules in the current working set.
    """
    from omgui.gui.gui_services import srv_mws

    return srv_mws.add_prop(prop_list_or_df, prop_name)


def clear(force: bool = False) -> None:
    """
    Clear the current molecule working set.
    """
    from omgui.gui.gui_services import srv_molecules

    srv_molecules.clear_mws(force)


# endregion
# ------------------------------------
# region - Getters
# ------------------------------------


def get() -> list[dict[str, Any]]:
    """
    Get the current molecule working set.
    """
    return ctx().mws()


def get_names() -> list[str]:
    """
    Get list of molecule names from your working set.
    """
    from omgui.gui.workers.smol_transformers import molset_to_names_list

    mws = ctx().mws()
    return molset_to_names_list(mws)


def get_smiles() -> list[str]:
    """
    Get list of molecule SMILES from your working set.
    """
    from omgui.gui.workers.smol_transformers import molset_to_smiles_list

    mws = ctx().mws()
    return molset_to_smiles_list(mws)


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


# endregion
# ------------------------------------
