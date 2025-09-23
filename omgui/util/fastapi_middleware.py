from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.requests import Request
from starlette.status import HTTP_301_MOVED_PERMANENTLY


class TrailingSlashMiddleware(BaseHTTPMiddleware):
    """
    This middleware forwards all paths with a trailing slash to
    the alternative path without.

    This is needed because, due to the catch-all forward routing all
    non-recognized paths to the Vue router via index.html, the default
    redirect_slashes=True for FastAPI is not working.
    """

    async def dispatch(self, request: Request, call_next):
        # Check if the path ends with a slash and is not the root.
        if request.url.path.endswith("/") and len(request.url.path) > 1:
            # Reconstruct the URL without the trailing slash, but keep query and hash.
            new_path = request.url.path.rstrip("/")
            new_url = f"{new_path}{request.url.query and '?' + request.url.query or ''}{request.url.fragment and '#' + request.url.fragment or ''}"

            return RedirectResponse(url=new_url, status_code=HTTP_301_MOVED_PERMANENTLY)
        return await call_next(request)
