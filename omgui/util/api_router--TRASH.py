from typing import Callable
from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable


class CustomAPIRouter(FastAPIRouter):
    pass


# class CustomAPIRouter(FastAPIRouter):
#     """
#     A custom APIRouter that creates alternative routes with or without
#     a trailing slash for every existing route, and forwards the one with
#     the trailing slash to the one without.

#     This is needed because, due to the catch-all forward routing all
#     non-recognized paths to the Vue router via index.html, the default
#     redirect_slashes=True for FastAPI is not working.
#     """

#     def api_route(
#         self, path: str, *, include_in_schema: bool = True, **kwargs
#     ) -> Callable[[DecoratedCallable], DecoratedCallable]:
#         # Strip the trailing slash from the provided path
#         if path.endswith("/"):
#             alternate_path = path
#             path = path.rstrip("/")
#         else:
#             alternate_path = path + "/"

#         # Add the route without the trailing slash
#         super().api_route(path, include_in_schema=include_in_schema, **kwargs)

#         # Add the route with the trailing slash
#         return super().api_route(alternate_path, include_in_schema=False, **kwargs)
