"""
Molecule working set functions for OMGUI API endpoints.
"""

# Std
import pandas as pd

# OMGUI
from omgui import ctx
from omgui.spf import spf
from omgui.gui.workers import smol_functions
from omgui.util import exceptions as omg_exc
from omgui.util.general import confirm_prompt


def add_mol(
    identifier: str = None,
    smol: dict = None,
    enrich: bool = None,
    silent: bool = False,
) -> bool:
    """
    Add a molecule to the molecule working set.

    Takes either an identifier or a mol object.
    """

    # Todo: add pydantic type for mol and validate

    # Invalid input
    if not smol and not identifier:
        raise omg_exc.InvalidMoleculeInput(
            "Either a molecule object or an identifier must be provided."
        )

    # Default enrich to True for identifiers and False for smol objects
    enrich = (smol is None) if enrich is None else enrich

    # Smol object -> enrich if requested
    if smol:
        # Maybe enrich with PubChem data
        if enrich:
            _, identifier = smol_functions.get_best_available_identifier(smol)
            smol_enriched = smol_functions.find_smol(identifier, enrich=True)
            if smol_enriched:
                smol = smol_functions.merge_smols(smol, smol_enriched)

    # Identifier -> enrich by default
    else:
        smol = smol_functions.find_smol(identifier, enrich=enrich)

    # Fail
    if not smol:
        return False

    # -- smol is defined --

    name = smol_functions.get_smol_name(smol)
    inchikey = smol.get("identifiers", {}).get("inchikey")

    # Already in mws -> skip
    if smol_functions.get_smol_from_mws(inchikey) is not None:
        if not silent:
            spf.success(f"Molecule <yellow>{name}</yellow> already in working set")
        return True

    # Add to working set
    ctx().mws_add(smol)
    if not silent:
        spf.success(f"Molecule <yellow>{name}</yellow> was added")
    return True


def remove_mol(identifier: str = None, smol: dict = None, silent=False):
    """
    Remove a molecule from your molecule working set.

    Takes either an identifier or a mol object.
    Identifier is slow because the molecule data has to be loaded from PubChem.
    """
    if not smol and not identifier:
        raise omg_exc.InvalidMoleculeInput(
            "Either a molecule object or an identifier must be provided."
        )

    # Create molecule object if only identifier is provided
    if not smol:
        smol = smol_functions.get_smol_from_mws(identifier)

    # -- smol is defined --

    name = smol_functions.get_smol_name(smol)
    inchikey = smol.get("identifiers", {}).get("inchikey")

    try:
        # Find matching molecule
        for i, item in enumerate(ctx().mws()):
            if item.get("identifiers", {}).get("inchikey") == inchikey:

                # Remove from mws
                ctx().mws_remove(i)

                # Feedback
                if not silent:
                    spf.success(f"Molecule <yellow>{name}</yellow> was removed")
                return True

        # Not found
        if not silent:
            spf.error(f"Molecule <yellow>{name}</yellow> not found in working set")
        return False

    except Exception as err:  # pylint: disable=broad-except
        if not silent:
            spf.error([f"Molecule <yellow>{name}</yellow> failed to be removed", err])
        return False


def is_mol_present(smol):
    """
    Check if a molecule is stored in your molecule working set.
    """

    # Get best available identifier
    _, identifier = smol_functions.get_best_available_identifier(smol)

    # Check if it's in the working set
    present = bool(smol_functions.get_smol_from_mws(identifier))
    return present


def add_prop(prop_list_or_df: list[str] | pd.DataFrame, prop_name: str = None) -> None:
    """
    Add property to molecules in the current working set.

    You can provide either:
    1. A list of property values and a property name (the list length must match
       the number of molecules in the working set)
    2. A pandas DataFrame with the following columns:
       - subject or smiles: SMILES molecule identifier
       - prop or property: property name
       - val, value or result: property value
    """
    from omgui.util.logger import get_logger
    from omgui.gui.gui_services import srv_mws
    from omgui.gui.workers.smol_functions import get_best_available_smiles

    logger = get_logger()
    mws = ctx().mws()

    # List of values + prop name
    if isinstance(prop_list_or_df, list) and prop_name:
        prop_list = prop_list_or_df
        if len(prop_list_or_df) != len(mws):
            spf.error(
                f"Length of property list ({len(prop_list)}) does not match number of molecules in working set ({len(mws)})."
            )
            return False
        for mol in mws:
            val = prop_list.pop(0)
            mol["properties"][prop_name] = val
            logger.info(
                "%s. Adding property <yellow>%s</yellow>: %s to molecule <yellow>%s</yellow>.",
                len(mws) - len(prop_list),
                prop_name,
                val,
                mol.get("name", get_best_available_smiles(mol)),
            )

        srv_mws.save()
        return True

    # DataFrame with subject/smiles + prop/property + val/value/result columns
    elif isinstance(prop_list_or_df, pd.DataFrame):
        df = prop_list_or_df
        df_columns_lower = [col.lower() for col in df.columns]
        fail = False

        # fmt: off
        # Validate dataframe structure
        if not any(val in df_columns_lower for val in ["subject", "smiles"]):
            fail = True
            spf.error("DataFrame must contain a <yellow>subject<yellow> column with SMILES values.")
        if not any(val in df_columns_lower for val in ["prop", "property"]):
            fail = True
            spf.error("DataFrame must contain a <yellow>prop<yellow> column with property names.")
        if not any(val in df_columns_lower for val in ["val", "value", "result"]):
            fail = True
            spf.error("DataFrame must contain a <yellow>val<yellow> column with property values.")
        if fail:
            return False
        # fmt: on

        # Define column names
        subject_col = "subject" if "subject" in df.columns else "smiles"
        property_col = "prop" if "prop" in df.columns else "property"
        value_col = (
            "val"
            if "val" in df.columns
            else ("value" if "value" in df.columns else "result")
        )

        for _, row in df.iterrows():
            subject = row[subject_col]
            prop_name = row[property_col]
            val = row[value_col]

            # Find the molecule in the working set
            mol_found = False
            for mol in mws:
                if (
                    mol.get("name") == subject
                    or get_best_available_smiles(mol) == subject
                ):
                    mol["properties"][prop_name] = val
                    logger.info(
                        "%s. Adding property <yellow>%s</yellow>: %s to molecule <yellow>%s</yellow>.",
                        len(mws) - len(prop_list),
                        prop_name,
                        val,
                        mol.get("name", get_best_available_smiles(mol)),
                    )
                    mol_found = True
                    break
            if not mol_found:
                spf.warning(
                    f"Skipping molecule with identifier <yellow>{subject}</yellow>, not found in working set."
                )

        srv_mws.save()
        return True
    else:
        spf.error(
            [
                "Invalid input: provide either:\n1. List of property values with a property name\n2. Pandas DataFrame with required columns.",
                "Example 1: add_props(['val1', 'val2'], prop_name='MyProp')",
                "Example 2: add_props(df) where df has the required 'subject', 'prop' and 'val' columns",
            ]
        )
        return False


def save() -> None:
    """
    Save changes to the molecule working set.
    """
    ctx().save()


def clear(force: bool = False):
    """
    Clear the molecule working set.
    """
    count = len(ctx().mws())
    if count == 0:
        spf.warning("No molecules to clear")
        return True
    if force or confirm_prompt(f"Are you sure you want to clear {count} molecules?"):
        ctx().mws_clear()
        spf.success("✅ Molecule working set cleared")
        return True
