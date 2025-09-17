# pylint: disable=missing-function-docstring

"""
This file contains all the API endpoints consumed by the GUI.

http://0.0.0.0:8024/api/v1/<endpoint>
"""

from urllib.parse import unquote
from fastapi import APIRouter, Request, status

# Service modules
from gui_services.general import GUIGeneralService
from gui_services.file_system import GUIFileSystemService
from gui_services.molecules import GUIMoleculesService
from gui_services.results import GUIResultService
from gui_services.dataframes import GUIDataframeService

# Various
import context

from helpers import logger
from helpers.exceptions import (
    InvalidMoleculeInput,
    InvalidMolset,
    NoResult,
    FailedOperation,
    CacheFileNotFound,
)


def create_router(ctx: context.Context) -> APIRouter:

    router = APIRouter()

    general_srv = GUIGeneralService(ctx)
    file_system_srv = GUIFileSystemService(ctx)
    molecules_srv = GUIMoleculesService(ctx)
    result_srv = GUIResultService(ctx)
    dataframe_srv = GUIDataframeService(ctx)

    api_v1 = "/api/v1"

    # ------------------------------------
    # region - General
    # ------------------------------------

    @router.get(f"{api_v1}/")
    async def landing():
        return general_srv.landing()

    @router.get(f"{api_v1}/health")
    async def health():
        return general_srv.health()

    @router.get(f"{api_v1}/settings")
    async def settings():
        return general_srv.ctx

    @router.post(f"{api_v1}/exec-command")
    async def exec_command(request: Request):
        body = await request.json()
        command = body.get("command")
        return general_srv.exec_command(command)

    # endregion
    # ------------------------------------
    # region - Context
    # ------------------------------------

    @router.get(f"{api_v1}/get-workspace-name")
    async def get_workspace_name():
        return ctx.workspace

    @router.get(f"{api_v1}/get-workspaces")
    async def get_workspaces():
        return ctx.workspaces()

    @router.post(f"{api_v1}/set-workspace")
    async def set_workspace(request: Request):
        body = await request.json()
        workspace_name = body.get("workspace", "")
        return ctx.set_workspace(workspace_name)

    @router.post(f"{api_v1}/create-workspace")
    async def create_workspace(request: Request):
        body = await request.json()
        workspace_name = body.get("workspace", "")
        return ctx.create_workspace(workspace_name)

    # endregion
    # ------------------------------------
    # region - File system
    # ------------------------------------

    @router.post(f"{api_v1}/get-files")
    async def get_files(request: Request):
        body = await request.json()
        path = unquote(body.get("path", ""))
        return file_system_srv.get_files(path)

    @router.post(f"{api_v1}/get-file")
    async def get_file(request: Request):
        body = await request.json()
        path = unquote(body.get("path"), "")
        query = body.get("query", {})
        return file_system_srv.get_file(path, query)

    @router.post(f"{api_v1}/open-file-os")
    async def open_file_os(request: Request):
        body = await request.json()
        path_absolute = unquote(body.get("path_absolute", ""))
        return file_system_srv.open_file_os(path_absolute)

    @router.post(f"{api_v1}/delete-file")
    async def delete_file(request: Request):
        body = await request.json()
        path_absolute = unquote(body.get("path_absolute", ""))
        return file_system_srv.delete_file(path_absolute)

    # endregion
    # ------------------------------------
    # region - Molecules - Small molecules
    # ------------------------------------

    @router.post(f"{api_v1}/get-smol-data")
    async def get_smol_data(request: Request):
        body = await request.json()
        identifier = body.get("identifier")
        return molecules_srv.get_smol_data(identifier)

    @router.post(f"{api_v1}/get-smol-viz-data", status_code=status.HTTP_200_OK)
    async def get_smol_viz_data(request: Request):
        body = await request.json()
        inchi_or_smiles = body.get("inchi_or_smiles")
        return molecules_srv.get_smol_viz_data(inchi_or_smiles)

    @router.post(f"{api_v1}/get-mol-data-from-molset")
    async def get_mol_data_from_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        index = body.get("index", 1)
        return molecules_srv.get_mol_data_from_molset(cache_id, index)

    @router.post(f"{api_v1}/enrich-smol")
    async def enrich_smol(request: Request):
        body = await request.json()
        smol = body.get("smol")
        return molecules_srv.enrich_smol(smol)

    @router.post(f"{api_v1}/save-smol-as-{{ext}}")
    async def save_smol_as(ext: str, request: Request):
        body = await request.json()
        smol = body.get("smol")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        force = body.get("force", False)

        # fmt: off
        # Map ext to the correct molecules_api method
        if ext == "json":
            return molecules_srv.save_mol(smol, path, new_file, force, format_as="mol_json")
        elif ext == "sdf":
            return molecules_srv.save_mol(smol, path, new_file, force, format_as="sdf")
        elif ext == "csv":
            return molecules_srv.save_mol(smol, path, new_file, force, format_as="csv")
        elif ext == "mdl":
            return molecules_srv.save_mol(smol, path, new_file, force, format_as="mdl")
        elif ext == "smiles":
            return molecules_srv.save_mol(smol, path, new_file, force, format_as="smiles")
        else:
            return f"Unknown file extension: {ext}", 400
        # fmt: on

    # endregion
    # ------------------------------------
    # region - Molecules - Molsets
    # ------------------------------------

    @router.post(f"{api_v1}/get-molset")
    async def get_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        query = body.get("query", {})
        return molecules_srv.get_molset(cache_id, query)

    @router.post(f"{api_v1}/remove-from-molset")
    async def remove_from_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        indices = body.get("indices", [])
        query = body.get("query", {})
        return molecules_srv.remove_from_molset(cache_id, indices, query)

    @router.post(f"{api_v1}/clear-molset-working-copy")
    async def clear_molset_working_copy(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        return molecules_srv.clear_molset_working_copy(cache_id)

    @router.post(f"{api_v1}/update-molset")
    async def update_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = False
        return molecules_srv.save_molset(cache_id, path, new_file)

    @router.post(f"{api_v1}/save-molset-as-json")
    async def save_molset_as_json(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "molset_json"
        return molecules_srv.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-sdf")
    async def save_molset_as_sdf(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "sdf"
        remove_invalid_mols = body.get("removeInvalidMols", False)
        return molecules_srv.save_molset(
            cache_id, path, new_file, format_as, remove_invalid_mols
        )

    @router.post(f"{api_v1}/save-molset-as-csv")
    async def save_molset_as_csv(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "csv"
        return molecules_srv.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-smiles")
    async def save_molset_as_smiles(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "smiles"
        return molecules_srv.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/replace-mol-in-molset")
    async def replace_mol_in_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        mol = body.get("mol")
        _context = body.get("context")
        format_as = "molset_json" if _context == "json" else _context
        return molecules_srv.replace_mol_in_molset(cache_id, path, mol, format_as)

    # endregion
    # ------------------------------------
    # region - Molecules - Macromolecules
    # ------------------------------------

    @router.post(f"{api_v1}/get-mmol-data")
    async def get_mmol_data(request: Request):
        body = await request.json()
        identifier = body.get("identifier")
        return molecules_srv.get_mmol_data(identifier)

    @router.post(f"{api_v1}/save-mmol-as-{{ext}}")
    async def save_mmol_as(ext: str, request: Request):
        body = await request.json()
        mmol = body.get("mmol")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        force = body.get("force", False)

        # fmt: off
        # Map ext to the correct molecules_api method
        if ext == "json":
            return molecules_srv.save_mol(mmol, path, new_file, force, format_as="mmol_json")
        elif ext == "cif":
            return molecules_srv.save_mol(mmol, path, new_file, force, format_as="cif")
        elif ext == "pdb":
            return molecules_srv.save_mol(mmol, path, new_file, force, format_as="pdb")
        else:
            return f"Unknown extension: {ext}", 400
        # fmt: on

    # endregion
    # ------------------------------------
    # region - Result
    # ------------------------------------

    @router.post(f"{api_v1}/get-result")
    async def get_result(request: Request):
        body = await request.json()
        query = body.get("query", {})
        return result_srv.get_result(query)

    @router.post(f"{api_v1}/update-result-molset")
    async def update_result_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId", "")
        return result_srv.update_result_molset(cache_id)

    # endregion
    # ------------------------------------
    # region - Molecule Working Set
    # ------------------------------------

    @router.post(f"{api_v1}/get-molset-mws")
    async def get_molset_mws(request: Request):
        body = await request.json()
        query = body.get("query", {})
        return molecules_srv.get_molset_mws(query)

    @router.post(f"{api_v1}/update-molset-mws")
    async def update_molset_mws(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = False
        format_as = "mws"
        return molecules_srv.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/add-mol-to-mws")
    async def add_mol_to_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        success = molecules_srv.add_mol_to_mws(smol=smol)
        if not success:
            raise FailedOperation("Failed to add molecule to your working set.")
        else:
            return True

    @router.post(f"{api_v1}/remove-mol-from-mws")
    async def remove_mol_from_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        success = molecules_srv.remove_mol_from_mws(smol=smol)
        if not success:
            raise FailedOperation("Failed to remove molecule from your working set.")
        else:
            return True

    @router.post(f"{api_v1}/check-mol-in-mws")
    async def check_mol_in_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        present = molecules_srv.check_mol_in_mws(smol)
        return {"status": present}

    # endregion
    # ------------------------------------
    # region - Dataframes
    # ------------------------------------

    @router.post(f"{api_v1}/get-dataframe/{{df_name}}")
    async def get_dataframe(df_name: str, request: Request):
        body = await request.json()
        query = body.get("query", {})
        return dataframe_srv.get_dataframe(df_name, query)

    @router.post(f"{api_v1}/update-dataframe-molset/{{df_name}}")
    async def update_dataframe_molset(df_name: str, request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        return dataframe_srv.update_dataframe_molset(df_name, cache_id)

    # endregion
    # ------------------------------------

    return router
