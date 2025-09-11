from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from exceptions import (
    InvalidMoleculeInput,
    InvalidMolset,
    NoResult,
    FailedOperation,
    CacheFileNotFound,
)


async def value_error_handler(request: Request, err: ValueError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Invalid value provided.",
            "error": str(err),
        },
    )


async def invalid_mol_input_handler(request: Request, err: InvalidMoleculeInput):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "message": "The provided molecule is not in valid format.",
            "error": str(err),
        },
    )


async def invalid_molset_handler(request: Request, err: InvalidMolset):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "message": "The provided molset is not valid.",
            "error": str(err),
        },
    )


async def no_result_handler(request: Request, err: NoResult):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "No result was obtained.",  # %%
            "error": str(err),
        },
    )


async def failed_operation_handler(request: Request, err: FailedOperation):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "The operation failed to complete successfully.",
            "error": str(err),
        },
    )


async def save_file_exists_handler(request: Request, err: FileExistsError):
    # Note: We can't access `path` here easily, but you can pass it in the exception's args
    return JSONResponse(
        status_code=HTTP_409_CONFLICT,
        content={
            "message": "A file with this name already exists.",
            "error": str(err),
        },
    )


async def save_file_not_found_handler(request: Request, err: FileNotFoundError):
    return JSONResponse(
        status_code=HTTP_404_NOT_FOUND,
        content={
            "message": "The file you're trying to save is not found.",
            "error": str(err),
        },
    )


async def cache_file_not_found_handler(request: Request, err: CacheFileNotFound):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={
            "message": "The cached working copy is not found.",
            "error": str(err),
        },
    )


async def permission_error_handler(request: Request, err: PermissionError):
    return JSONResponse(
        status_code=HTTP_403_FORBIDDEN,
        content={"message": "Permission denied.", "error": str(err)},
    )


async def catch_all_handler(request: Request, err: Exception):
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An internal server error occurred.", "error": str(err)},
    )


def register_exception_handlers(app):
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(InvalidMoleculeInput, invalid_mol_input_handler)
    app.add_exception_handler(NoResult, no_result_handler)
    app.add_exception_handler(FailedOperation, failed_operation_handler)
    app.add_exception_handler(FileExistsError, save_file_exists_handler)
    app.add_exception_handler(FileNotFoundError, save_file_not_found_handler)
    app.add_exception_handler(CacheFileNotFound, cache_file_not_found_handler)
    app.add_exception_handler(PermissionError, permission_error_handler)
    app.add_exception_handler(Exception, catch_all_handler)
