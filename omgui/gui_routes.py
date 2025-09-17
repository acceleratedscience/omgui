# pylint: disable=missing-function-docstring

"""
This file contains all the API endpoints consumed by the GUI.

http://0.0.0.0:8024/api/v1/<endpoint>
"""

from urllib.parse import unquote
from fastapi import APIRouter, Request, status

# Service modules
from omgui.gui_services import srv_general
from omgui.gui_services import srv_file_system
from omgui.gui_services import srv_molecules
from omgui.gui_services import srv_result
from omgui.gui_services import srv_dataframe

# Various
from omgui import context
from omgui.helpers import logger
from omgui.helpers import exceptions as omg_exc


def create_router(ctx: context.Context) -> APIRouter:

    router = APIRouter()

    api_v1 = "/api/v1"

    # ------------------------------------
    # region - General
    # ------------------------------------

    @router.get(f"{api_v1}/")
    async def landing():
        return srv_general.landing()

    @router.get(f"{api_v1}/health")
    async def health():
        return srv_general.health()

    @router.get(f"{api_v1}/settings")
    async def settings():
        return srv_general.ctx

    @router.post(f"{api_v1}/exec-command")
    async def exec_command(request: Request):
        body = await request.json()
        command = body.get("command")
        return srv_general.exec_command(command)

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
        return srv_file_system.get_files(path)

    @router.post(f"{api_v1}/get-file")
    async def get_file(request: Request):
        body = await request.json()
        print(body.get("path"))
        print(unquote(body.get("path")))
        path = unquote(body.get("path", ""))
        query = body.get("query", {})
        return srv_file_system.get_file(path, query)

    @router.post(f"{api_v1}/open-file-os")
    async def open_file_os(request: Request):
        body = await request.json()
        path_absolute = unquote(body.get("path_absolute", ""))
        return srv_file_system.open_file_os(path_absolute)

    @router.post(f"{api_v1}/delete-file")
    async def delete_file(request: Request):
        body = await request.json()
        path_absolute = unquote(body.get("path_absolute", ""))
        return srv_file_system.delete_file(path_absolute)

    # endregion
    # ------------------------------------
    # region - Molecules - Small molecules
    # ------------------------------------

    @router.post(f"{api_v1}/get-smol-data")
    async def get_smol_data(request: Request):
        body = await request.json()
        identifier = body.get("identifier")
        return srv_molecules.get_smol_data(identifier)

    @router.post(f"{api_v1}/get-smol-viz-data", status_code=status.HTTP_200_OK)
    async def get_smol_viz_data(request: Request):
        body = await request.json()
        inchi_or_smiles = body.get("inchi_or_smiles")
        return srv_molecules.get_smol_viz_data(inchi_or_smiles)

    @router.post(f"{api_v1}/get-mol-data-from-molset")
    async def get_mol_data_from_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        index = body.get("index", 1)
        return srv_molecules.get_mol_data_from_molset(cache_id, index)

    @router.post(f"{api_v1}/enrich-smol")
    async def enrich_smol(request: Request):
        body = await request.json()
        smol = body.get("smol")
        return srv_molecules.enrich_smol(smol)

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
            return srv_molecules.save_mol(smol, path, new_file, force, format_as="mol_json")
        elif ext == "sdf":
            return srv_molecules.save_mol(smol, path, new_file, force, format_as="sdf")
        elif ext == "csv":
            return srv_molecules.save_mol(smol, path, new_file, force, format_as="csv")
        elif ext == "mdl":
            return srv_molecules.save_mol(smol, path, new_file, force, format_as="mdl")
        elif ext == "smiles":
            return srv_molecules.save_mol(smol, path, new_file, force, format_as="smiles")
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
        return srv_molecules.get_molset(cache_id, query)

    @router.post(f"{api_v1}/remove-from-molset")
    async def remove_from_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        indices = body.get("indices", [])
        query = body.get("query", {})
        return srv_molecules.remove_from_molset(cache_id, indices, query)

    @router.post(f"{api_v1}/clear-molset-working-copy")
    async def clear_molset_working_copy(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        return srv_molecules.clear_molset_working_copy(cache_id)

    @router.post(f"{api_v1}/update-molset")
    async def update_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = False
        return srv_molecules.save_molset(cache_id, path, new_file)

    @router.post(f"{api_v1}/save-molset-as-json")
    async def save_molset_as_json(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "molset_json"
        return srv_molecules.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-sdf")
    async def save_molset_as_sdf(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "sdf"
        remove_invalid_mols = body.get("removeInvalidMols", False)
        return srv_molecules.save_molset(
            cache_id, path, new_file, format_as, remove_invalid_mols
        )

    @router.post(f"{api_v1}/save-molset-as-csv")
    async def save_molset_as_csv(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "csv"
        return srv_molecules.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-smiles")
    async def save_molset_as_smiles(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "smiles"
        return srv_molecules.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/replace-mol-in-molset")
    async def replace_mol_in_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        mol = body.get("mol")
        _context = body.get("context")
        format_as = "molset_json" if _context == "json" else _context
        return srv_molecules.replace_mol_in_molset(cache_id, path, mol, format_as)

    # endregion
    # ------------------------------------
    # region - Molecules - Macromolecules
    # ------------------------------------

    @router.post(f"{api_v1}/get-mmol-data")
    async def get_mmol_data(request: Request):
        body = await request.json()
        identifier = body.get("identifier")
        return srv_molecules.get_mmol_data(identifier)

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
            return srv_molecules.save_mol(mmol, path, new_file, force, format_as="mmol_json")
        elif ext == "cif":
            return srv_molecules.save_mol(mmol, path, new_file, force, format_as="cif")
        elif ext == "pdb":
            return srv_molecules.save_mol(mmol, path, new_file, force, format_as="pdb")
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
        return srv_result.get_result(query)

    @router.post(f"{api_v1}/update-result-molset")
    async def update_result_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId", "")
        return srv_result.update_result_molset(cache_id)

    # endregion
    # ------------------------------------
    # region - Molecule Working Set
    # ------------------------------------

    @router.post(f"{api_v1}/get-molset-mws")
    async def get_molset_mws(request: Request):
        body = await request.json()
        query = body.get("query", {})
        return srv_molecules.get_molset_mws(query)

    @router.post(f"{api_v1}/update-molset-mws")
    async def update_molset_mws(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = False
        format_as = "mws"
        return srv_molecules.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/add-mol-to-mws")
    async def add_mol_to_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        success = srv_molecules.add_mol_to_mws(smol=smol)
        if not success:
            raise omg_exc.FailedOperation("Failed to add molecule to your working set.")
        else:
            return True

    @router.post(f"{api_v1}/remove-mol-from-mws")
    async def remove_mol_from_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        success = srv_molecules.remove_mol_from_mws(smol=smol)
        if not success:
            raise omg_exc.FailedOperation(
                "Failed to remove molecule from your working set."
            )
        else:
            return True

    @router.post(f"{api_v1}/check-mol-in-mws")
    async def check_mol_in_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        present = srv_molecules.check_mol_in_mws(smol)
        return {"status": present}

    # endregion
    # ------------------------------------
    # region - Dataframes
    # ------------------------------------

    @router.post(f"{api_v1}/get-dataframe/{{df_name}}")
    async def get_dataframe(df_name: str, request: Request):
        body = await request.json()
        query = body.get("query", {})
        return srv_dataframe.get_dataframe(df_name, query)

    @router.post(f"{api_v1}/update-dataframe-molset/{{df_name}}")
    async def update_dataframe_molset(df_name: str, request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        return srv_dataframe.update_dataframe_molset(df_name, cache_id)

    # endregion
    # ------------------------------------

    return router
