"""
Molecules API
"""

import os
import json
import shutil

# Small molecule functions
from workers.smol_functions import (
    get_smol_from_pubchem,
    create_molset_cache_file,
    assemble_cache_path,
    read_molset_from_cache,
    find_smol,
    mws_add,
    mws_remove,
    get_smol_from_mws,
    get_best_available_identifier,
    get_best_available_smiles,
    merge_smols,
)
from workers.smol_transformers import (
    smol2svg,
    smol2mdl,
    molset2dataframe,
    write_dataframe2sdf,
    write_dataframe2csv,
)

# Macromolecule functions
from workers.mmol_functions import mmol_from_identifier
from workers.mmol_transformers import mmol2pdb, mmol2cif, cif2mmol

# Various
from helpers import logger, JSONDecimalEncoder
from helpers.molecules import create_molset_response
from helpers.exceptions import (
    InvalidMoleculeInput,
    InvalidMolset,
    NoResult,
    FailedOperation,
    CacheFileNotFound,
)


class GUIMoleculesApiService:
    """
    Molecule functions for OMGUI API endpoints.
    """

    def __init__(self, cmd_pointer):
        self.cmd_pointer = cmd_pointer

    # ------------------------------------
    # region - Small molecules
    # ------------------------------------

    def get_smol_data(self, identifier):
        """
        Get molecule data, plus MDL and SVG.
        Used when requesting a molecule by its identifier.
        """
        smol = find_smol(self.cmd_pointer, identifier)

        # Fail
        if not smol:
            raise NoResult(f"No small molecule found with identifier '{identifier}'")

        # Success
        return smol

    def get_smol_viz_data(self, inchi_or_smiles):
        """
        Get a molecule's SVG and MDL data, which can be used to render 2D and 3D visualizations.
        """
        try:
            svg = smol2svg(inchi_or_smiles=inchi_or_smiles)
            mdl = smol2mdl(inchi_or_smiles=inchi_or_smiles)

        except (TypeError, ValueError) as err:
            raise InvalidMoleculeInput(
                f"Failed to generate visualisation data for '{inchi_or_smiles}'. Input should be SMILES or InChI."
            ) from err

        if not svg and not mdl:
            raise NoResult(
                f"Failed to generate visualisation data for '{inchi_or_smiles}'. No valid data could be generated."
            ) from err

        return {"mdl": mdl, "svg": svg}

    def get_mol_data_from_molset(self, cache_id, index=1):
        """
        Get a molecule from a molset file.
        """
        cache_path = assemble_cache_path(self.cmd_pointer, "molset", cache_id)

        with open(cache_path, "r", encoding="utf-8") as f:
            molset = json.load(f)

        return molset[index - 1]

    ##

    def add_mol_to_mws(self, smol):
        """
        Add a molecule to the molecule working set.

        Takes either an identifier or a mol object.
        Identifier is slow because the molecule data has to be loaded from PubChem.
        """
        # Get best available identifier
        _, identifier = get_best_available_identifier(smol)

        # Enrich molecule with PubChem data
        smol_enriched = find_smol(self.cmd_pointer, identifier, basic=True)
        if smol_enriched:
            smol = merge_smols(smol, smol_enriched)

        # Add it to the working set
        success = mws_add(self.cmd_pointer, smol, force=True)

        if not success:
            raise FailedOperation("Failed to add molecule to your working set.")
        else:
            return True

    def remove_mol_from_mws(self, smol):
        """
        Remove a molecule from your molecule working set.

        Takes either an identifier or a mol object.
        Identifier is slow because the molecule data has to be loaded from PubChem.
        """
        # Remove it from the working set
        success = mws_remove(self.cmd_pointer, smol, force=True)

        if not success:
            raise FailedOperation("Failed to remove molecule from your working set.")
        else:
            return True

    def check_mol_in_mws(self, smol):
        """
        Check if a molecule is stored in your molecule working set.
        """

        # Get best available identifier
        _, identifier = get_best_available_identifier(smol)

        # Check if it's in the working set
        present = bool(get_smol_from_mws(self.cmd_pointer, identifier))
        return present

    def enrich_smol(self, smol):
        """
        Enrich a molecule with PubChem data.
        """

        # Get best available identifier.
        _, identifier = get_best_available_identifier(smol)

        # Enrich molecule withg PubChem data.
        smol_enriched = get_smol_from_pubchem(identifier)
        if smol_enriched:
            smol = merge_smols(smol, smol_enriched)

        return smol

    # endregion
    # ------------------------------------
    # region - Macromolecules
    # ------------------------------------

    def get_mmol_data(self, identifier):
        """
        Get macromolecule data.
        Used when requesting a macromolecule by its identifier.
        """
        success, cif_data = mmol_from_identifier(identifier)

        if not success:
            raise NoResult(f"No macromolecule found with identifier '{identifier}'")
        else:
            mmol = cif2mmol(cif_data)
            return mmol

    # endregion
    # ------------------------------------
    # region - Molecules shared
    # ------------------------------------

    def save_mol(self, mol, path, new_file=True, force=False, format_as="mol_json"):
        """
        Save a molecule to a file, in the specified format.

        Parameters
        ----------
        mol: dict
            molecule object (smol or mmol)
        path: str
            destination file path
        new_file: bool
            whether to create a new file or update an existing one (default: True)
        force: bool
            whether to overwrite existing files (default: False)
        format_as: str
            file format to save as (default: "mol_json")
        """

        # Note: the new_file parameter is always true for now, but later on
        # when we let users add comments etc, we'll want to be able to update
        # existing files.

        # Detect smol or mmol format
        # TODO: implement a strict schema that can be validated
        smol = mol if "identifiers" in mol else None
        mmol = mol if "data" in mol else None

        if not smol and not mmol:
            raise InvalidMoleculeInput

        # Compile path
        workspace_path = self.cmd_pointer.workspace_path()
        file_path = workspace_path + "/" + path

        # Throw error when detination file (does not) exist(s).
        if path:
            if new_file:
                if os.path.exists(file_path) and not force:
                    raise FileExistsError(f"File path: {file_path}")
            else:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File path: {file_path}")

        # Small molecules
        # ------------------------------------
        if smol:

            # Save as .smol.json file.
            if format_as == "mol_json":
                # Write to file
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        smol, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder
                    )

            # Save as .sdf file.
            elif format_as == "sdf":
                df = molset2dataframe([smol], include_romol=True)
                write_dataframe2sdf(df, file_path)

            # Save as .csv file.
            elif format_as == "csv":
                df = molset2dataframe([smol])
                write_dataframe2csv(df, file_path)

            # Save as .mol file.
            elif format_as == "mdl":
                smol2mdl(smol, path=file_path)

            # Save as .smi file.
            elif format_as == "smiles":
                smiles = get_best_available_smiles(smol)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(smiles)

        # Macromolecules
        # ------------------------------------
        elif mmol:

            # Save as .mmol.json file.
            if format_as == "mmol_json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        mmol, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder
                    )

            # Save as .cif file.
            elif format_as == "cif":
                mmol2cif(mmol, path=file_path)

            # Save as .pdb file.
            elif format_as == "pdb":
                mmol2pdb(mmol, path=file_path)

        return True

    # endregion
    # ------------------------------------
    # region - Molsets
    # -----------------------------

    def get_molset(self, cache_id, query=None):
        """
        Get a cached molset, filtered by the query.
        Note: opening molset files is handled by fs_attach_file_data() in workers/file_system.py
        """
        # Read molset from cache.
        molset = read_molset_from_cache(self.cmd_pointer, cache_id)

        # Formulate response object.
        return create_molset_response(molset, query, cache_id)

    def get_molset_mws(self, query=None):
        """
        Get the list of molecules currently stored in the molecule working set.
        """
        if len(self.cmd_pointer.molecule_list) > 0:
            # Compile molset.
            molset = []
            for i, smol in enumerate(self.cmd_pointer.molecule_list):
                smol["index"] = i + 1
                molset.append(smol)

            # Create cache working copy.
            cache_id = create_molset_cache_file(self.cmd_pointer, molset)

            # Read molset from cache.
            molset = read_molset_from_cache(self.cmd_pointer, cache_id)

            # Formulate response object.
            return create_molset_response(molset, query, cache_id)

        else:
            return None

    ##

    def remove_from_molset(self, cache_id, indices, query=None):
        """
        Remove molecules from a molset's cached working copy.
        """

        if len(indices) == 0:
            raise ValueError("No indices provided")

        # Compile path
        cache_path = assemble_cache_path(self.cmd_pointer, "molset", cache_id)

        # Read file from cache
        with open(cache_path, "r", encoding="utf-8") as f:
            molset = json.load(f)

        # Remove molecules
        molset = [mol for mol in molset if mol.get("index") not in indices]

        # Write to cache
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(molset, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)

        # Create response object
        return create_molset_response(molset, query, cache_id)

    def clear_molset_working_copy(self, cache_id):
        """
        Clear a molset's cached working copy.
        """
        cache_path = assemble_cache_path(self.cmd_pointer, "molset", cache_id)

        if os.path.exists(cache_path):
            os.remove(cache_path)

        return True

    ##

    def save_molset(
        self,
        cache_id,
        path,
        new_file=False,
        format_as="molset_json",
        remove_invalid_mols=False,
    ):
        """
        Save a molset to a file, in the specified format.

        Parameters
        ----------
        new_file: bool
            Whether we're creating a new file or overwriting an existing one.
        format_as: 'molset_json' | 'sdf' | 'csv' | 'smiles'.
            The format to save the molset as.
        remove_invalid_mols: bool
            Whether to remove invalid molecules from the molset before saving.

        """
        # Compile path
        workspace_path = self.cmd_pointer.workspace_path()
        file_path = workspace_path + "/" + path
        cache_path = assemble_cache_path(self.cmd_pointer, "molset", cache_id)

        # Throw error when destination file (does not) exist(s)
        if path:
            if new_file:
                if os.path.exists(file_path):
                    raise FileExistsError(f"File path: {file_path}")
            else:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File path: {file_path}")

        if not os.path.exists(cache_path):
            raise CacheFileNotFound(f"Cache file path: {cache_path}")

        # For .molset.json files, we simply copy the cache file to the destination
        if format_as == "molset_json":
            shutil.copy(cache_path, file_path)
            return True

        # For all other formats, we need to read the
        # molset data into memory so we can transform it
        else:
            with open(cache_path, "r", encoding="utf-8") as f:
                molset = json.load(f)

        # Save as SDF file
        if format_as == "sdf":
            df = molset2dataframe(molset, remove_invalid_mols, include_romol=True)
            write_dataframe2sdf(df, file_path)

        # Save as CSV file
        elif format_as == "csv":
            df = molset2dataframe(molset, remove_invalid_mols)
            write_dataframe2csv(df, file_path)

        # Save as SMILES file
        elif format_as == "smiles":
            smiles_list = []
            missing_smiles = []
            for mol in molset:
                smiles = get_best_available_smiles(mol)
                if smiles:
                    smiles_list.append(smiles)
                else:
                    missing_smiles.append(mol["index"])

            # Return error if there are missing SMILES
            if missing_smiles:
                raise InvalidMolset(f"Missing SMILES for molecules: {missing_smiles}")

            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(smiles_list))

        elif format_as == "my-mols":
            # Read file from cache
            with open(cache_path, "r", encoding="utf-8") as f:
                molset = json.load(f)

            # Compile molset
            molecule_list = []
            for mol in molset:
                molecule_list.append(mol)

            self.cmd_pointer.molecule_list = molecule_list

        return True

    def replace_mol_in_molset(self, cache_id, path, mol, format_as):
        """
        Replace a molecule in a molset file.

        This first updates the cache working copy, then saves the
        changes to the actual molset file, or to the molecule working set.
        """
        # Compile path
        cache_path = assemble_cache_path(self.cmd_pointer, "molset", cache_id)

        # Read file from cache.
        with open(cache_path, "r", encoding="utf-8") as f:
            molset = json.load(f)

        # Replace molecule in molset working copy.
        index = mol.get("index")
        molset[index - 1] = mol

        # Write to cache.
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(molset, f, ensure_ascii=False, indent=4, cls=JSONDecimalEncoder)

        # Now the working copy is updated, we also update the molset.
        return self.save_molset(cache_id, path, new_file=False, format_as=format_as)

    # endregion
    # ------------------------------------
    # region - Helpers
    # ------------------------------------

    def _sort_mol(self, mol, sort_key):
        """
        Sorter function for a molset.

        Parameters
        ----------
        mol: dict
            A molecule object.
        sort_key: str
            The key of the category whose value we'll sort by.
            Eg. 'name' (identifier) or 'molecular_weight' (property).
        """
        if sort_key == "index":
            value = mol.get(sort_key)
        elif sort_key == "name":
            value = (mol.get("identifiers") or {}).get(sort_key)
        else:
            value = (mol.get("properties") or {}).get(sort_key)

        value = self.__prep_sort_value(value)

        # Returning a tuple will sort by the first value, then the
        # second, etc. This lets us group all none values on top.
        return (value is None, value)

    def __prep_sort_value(self, value):
        """
        Prepare a value for sorting by:
        - Converting strings to lowercase
        - Converting number strings to floats

        Parameters
        ----------
        value: str, int, float
            The value to prepare.
        """

        # Convert number strings to floats
        try:
            return float(value)
        except ValueError:
            pass

        # Convert strings to lowercase
        if isinstance(value, str):
            return value.lower()

        return value

    # endregion
    # ------------------------------------
