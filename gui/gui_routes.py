# pylint: disable=missing-function-docstring

"""
This file contains all the API endpoints consumed by the GUI.

http://0.0.0.0:8024/api/v1/<endpoint>
"""

from urllib.parse import unquote
from fastapi import APIRouter, Request, status

# API modules
from api.general_api import GeneralApi
from api.file_system_api import FileSystemApi
from api.molecules_api import MoleculesApi
from api.result_api import ResultApi
from api.dataframe_api import DataframeApi

# Various
from cmd_pointer import CmdPointerTemp, cmd_pointer


def create_router(cmd_pointer: CmdPointerTemp):

    router = APIRouter()

    general_api = GeneralApi(cmd_pointer)
    file_system_api = FileSystemApi(cmd_pointer)
    molecules_api = MoleculesApi(cmd_pointer)
    result_api = ResultApi(cmd_pointer)
    dataframe_api = DataframeApi(cmd_pointer)

    api_v1 = "/api/v1"

    # ------------------------------------
    # region - General
    # ------------------------------------

    @router.get(f"{api_v1}/")
    async def landing():
        return general_api.landing()

    @router.get(f"{api_v1}/health")
    async def health():
        return general_api.health()

    @router.post(f"{api_v1}/exec-command")
    async def exec_command(request: Request):
        body = await request.json()
        command = body.get("command")
        return general_api.exec_command(command)

    # endregion
    # ------------------------------------
    # region - File system
    # ------------------------------------

    @router.get(f"{api_v1}/get-workspaces")
    async def get_workspaces():
        return file_system_api.get_workspaces()

    @router.get(f"{api_v1}/get-workspace")
    async def get_workspace():
        return file_system_api.get_workspace()

    @router.post(f"{api_v1}/set-workspace")
    async def set_workspace(request: Request):
        body = await request.json()
        workspace_name = body.get("workspace", "")
        return file_system_api.set_workspace(workspace_name)

    @router.post(f"{api_v1}/get-workspace-files")
    async def get_workspace_files(request: Request):
        body = await request.json()
        path = unquote(body.get("path", ""))
        return file_system_api.get_workspace_files(path)

    @router.post(f"{api_v1}/get-file")
    async def get_file(request: Request):
        body = await request.json()
        path = unquote(body.get("path"), "")
        query = body.get("query", {})
        return file_system_api.get_file(path, query)

    @router.post(f"{api_v1}/open-file-os")
    async def open_file_os(request: Request):
        body = await request.json()
        path_absolute = unquote(body.get("path_absolute", ""))
        return file_system_api.open_file_os(path_absolute)

    @router.post(f"{api_v1}/delete-file")
    async def delete_file(request: Request):
        body = await request.json()
        path_absolute = unquote(body.get("path_absolute", ""))
        return file_system_api.delete_file(path_absolute)

    # endregion
    # ------------------------------------
    # region - Molecules - Small molecules
    # ------------------------------------

    @router.post(f"{api_v1}/get-smol-data")
    async def get_smol_data(request: Request):
        body = await request.json()
        identifier = body.get("identifier")
        return molecules_api.get_smol_data(identifier)

    @router.post(f"{api_v1}/get-smol-viz-data", status_code=status.HTTP_200_OK)
    async def get_smol_viz_data(request: Request):
        body = await request.json()
        inchi_or_smiles = body.get("inchi_or_smiles")
        return molecules_api.get_smol_viz_data(inchi_or_smiles)

    @router.post(f"{api_v1}/get-mol-data-from-molset")
    async def get_mol_data_from_molset(request: Request):
        body = await request.json()
        cache_id = body("cacheId")
        index = body("index", 1)
        return molecules_api.get_mol_data_from_molset(cache_id, index)

    @router.post(f"{api_v1}/add-mol-to-mws")
    async def add_mol_to_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        return molecules_api.add_mol_to_mws(smol)

    @router.post(f"{api_v1}/remove-mol-from-mws")
    async def remove_mol_from_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        return molecules_api.remove_mol_from_mws(smol)

    @router.post(f"{api_v1}/check-mol-in-mws")
    async def check_mol_in_mws(request: Request):
        body = await request.json()
        smol = body.get("mol")
        present = molecules_api.check_mol_in_mws(smol)
        return {"status": present}

    @router.post(f"{api_v1}/enrich-smol")
    async def enrich_smol(request: Request):
        body = await request.json()
        smol = body.get("smol")
        return molecules_api.enrich_smol(smol)

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
            return molecules_api.save_mol(smol, path, new_file, force, format_as="mol_json")
        elif ext == "sdf":
            return molecules_api.save_mol(smol, path, new_file, force, format_as="sdf")
        elif ext == "csv":
            return molecules_api.save_mol(smol, path, new_file, force, format_as="csv")
        elif ext == "mdl":
            return molecules_api.save_mol(smol, path, new_file, force, format_as="mdl")
        elif ext == "smiles":
            return molecules_api.save_mol(smol, path, new_file, force, format_as="smiles")
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
        return molecules_api.get_molset(cache_id, query)

    @router.post(f"{api_v1}/get-molset-mws")
    async def get_molset_mws(request: Request):
        body = await request.json()
        query = body.get("query", {})
        return molecules_api.get_molset_mws(query)

    @router.post(f"{api_v1}/remove-from-molset")
    async def remove_from_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        indices = body.get("indices", [])
        query = body.get("query", {})
        return molecules_api.remove_from_molset(cache_id, indices, query)

    @router.post(f"{api_v1}/clear-molset-working-copy")
    async def clear_molset_working_copy(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        return molecules_api.clear_molset_working_copy(cache_id)

    @router.post(f"{api_v1}/update-molset")
    async def update_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = False
        return molecules_api.save_molset(cache_id, path, new_file)

    @router.post(f"{api_v1}/update-molset-mws")
    async def update_molset_mws(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = False
        format_as = "my-mols"
        return molecules_api.update_molset_mws(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-json")
    async def save_molset_as_json(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "molset_json"
        return molecules_api.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-sdf")
    async def save_molset_as_sdf(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "sdf"
        remove_invalid_mols = body.get("removeInvalidMols", False)
        return molecules_api.save_molset(
            cache_id, path, new_file, format_as, remove_invalid_mols
        )

    @router.post(f"{api_v1}/save-molset-as-csv")
    async def save_molset_as_csv(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "csv"
        return molecules_api.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/save-molset-as-smiles")
    async def save_molset_as_smiles(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        new_file = body.get("newFile", False)
        format_as = "smiles"
        return molecules_api.save_molset(cache_id, path, new_file, format_as)

    @router.post(f"{api_v1}/replace-mol-in-molset")
    async def replace_mol_in_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId")
        path = unquote(body.get("path", ""))
        mol = body.get("mol")
        _context = body.get("context")
        format_as = "molset_json" if _context == "json" else _context
        return molecules_api.replace_mol_in_molset(cache_id, path, mol, format_as)

    # endregion
    # ------------------------------------
    # region - Molecules - Macromolecules
    # ------------------------------------

    @router.post(f"{api_v1}/get-mmol-data")
    async def get_mmol_data(request: Request):
        body = await request.json()
        identifier = body.get("identifier")
        return molecules_api.get_mmol_data(identifier)

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
            return molecules_api.save_mol(mmol, path, new_file, force, format_as="mmol_json")
        elif ext == "cif":
            return molecules_api.save_mol(mmol, path, new_file, force, format_as="cif")
        elif ext == "pdb":
            return molecules_api.save_mol(mmol, path, new_file, force, format_as="pdb")
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
        return result_api.get_result(query)

    @router.post(f"{api_v1}/update-result-molset")
    async def update_result_molset(request: Request):
        body = await request.json()
        cache_id = body.get("cacheId", "")
        return result_api.update_result_molset(cache_id)

    # endregion
    # ------------------------------------
    # region - Dataframes
    # ------------------------------------

    @router.post(f"{api_v1}/get-dataframe/{{df_name}}")
    async def get_dataframe(df_name: str, request: Request):
        body = await request.json()
        query = body.get("query", {})
        return dataframe_api.get_dataframe(df_name, query)

    @router.post(f"{api_v1}/update-dataframe-molset/{{df_name}}")
    async def update_dataframe_molset(df_name: str, request: Request):
        body = await request.json()
        cache_id = body("cacheId")
        return dataframe_api.update_dataframe_molset(df_name, cache_id)

    # endregion
    # ------------------------------------

    return router
