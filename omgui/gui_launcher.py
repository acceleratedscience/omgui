"""
This file contains the GUI launcher and installer.

The GUI is launched in a separate thread using werkzeug via ServerThread.
The launcher will either start up the GUI server, or open the GUI in a
browser if the server was already active.
"""

import os
import json
import time
import socket
import atexit
import uvicorn
import logging
import mimetypes
import webbrowser
import urllib.parse
from pathlib import Path
from threading import Thread


# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response

# omgui
from omgui import config, ctx
from omgui.gui_routes import gui_router
from omgui.util import gui_install
from omgui.util.jupyter import nb_mode
from omgui.util.general import next_avail_port, wait_for_port
from omgui.util.exception_handlers import register_exception_handlers
from omgui.spf import spf


GUI_SERVER = None
NOTEBOOK_MODE = nb_mode()

# Optional BASE_PATH configuration
# We always want it w/o leading slash, but with trailing slash
# See proxy_server.py for details
BASE_PATH = (config.base_path).strip("/") + "/" if config.base_path else ""


class GUIThread(Thread):
    """
    Thread class that allows us to shut down
    the sub-process from the main thread.
    """

    def __init__(self, app, host, port):
        super().__init__()
        self.app = app
        self.host = host
        self.port = port
        self.active = True
        self.server = None

    def run(self):
        config = uvicorn.Config(
            self.app, host=self.host, port=self.port, log_level="error"
        )
        self.server = uvicorn.Server(config)
        self.server.run()

    def is_running(self):
        """Check if the server is running."""
        return self.active

    def shutdown(self):
        """Shut the server down."""
        if self.server:
            self.server.should_exit = True
        self.join()
        self.active = False
        _print_shutdown_msg(self.host, self.port)


def gui_init(path=None, data=None, silent=False):
    """
    Check if the GUI is installed and start the server.

    If this GUI is not installed (openad-gui folder not present),
    suggest to install it, unless the user has chosen before not
    to be asked again (openad-gui folder present without index.html).

    Parameters
    ----------
    path : str, optional
        The path to load. If none is provided, the filebrowser is loaded.
    data : dict, optional
        A data dictionary that will be stringified, encoded and passed
        to the GUI via the ?data= query parameter.
        This is no longer used, but may be useful in the future.
    silent : bool, optional
        If True, we'll start the server without opening the browser.
        This is used when restarting the server.
    """
    # Jupyter: wrap up immediately
    if NOTEBOOK_MODE:
        _gui_init(path, data, silent=True)
        return

    # Terminal: keep alive main thread
    # --> allow Ctrl+C to stop it elegantly
    try:
        _gui_init(path, data, silent)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Ctrl+C was pressed --> atexit handles this
        pass
    finally:
        # Redundant, but to be safe
        cleanup()


def _gui_init(path=None, data=None, silent=False):
    # Install the GUI if needed
    gui_install.ensure()

    # Parse potential data into a URL string
    query = "?data=" + urllib.parse.quote(json.dumps(data)) if data else ""
    hash = ""

    # Launch the GUI
    _launch(path, query, hash, silent)


def _launch(path=None, query="", hash="", silent=False):
    """
    Launch the GUI web server in a separate thread.
    """

    global GUI_SERVER

    # If the server is already running, don't launch it again
    if GUI_SERVER and GUI_SERVER.is_running():
        _open_browser(GUI_SERVER.host, GUI_SERVER.port, path, query, hash, silent)
        return

    # Initialize FastAPI app
    app = FastAPI(title="OpenAD")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    # Include API routes
    app.include_router(gui_router, prefix="", tags=["GUI API"])

    # Shutdown route
    @app.get("/shutdown")
    async def shut_down():
        # Shutdown here needs to happen with a delay,
        # because this API call needs to finish before
        # the shutdown will execute.
        def delayed_shutdown():
            time.sleep(1)
            GUI_SERVER.shutdown()

        Thread(target=delayed_shutdown).start()
        return Response(content="OMGUI shutdown complete", status_code=200)

    # Note: we don't serve static assets, because we dynamically
    # replace "__BASE_PATH__/" in all static files:
    # - - -
    # from fastapi.staticfiles import StaticFiles
    # app.mount("/assets", StaticFiles(directory=gui_build / "assets"), name="assets")

    # Serve all other paths by pointing to index.html,
    # Vue router takes care of the rest.
    @app.get("/")
    @app.get("/{path:path}")
    async def serve(path: str = ""):
        try:
            gui_build_dir = Path(__file__).parents[0].resolve() / "dist"
            file_path = gui_build_dir / path

            if path != "" and file_path.exists():
                mime_type, _ = mimetypes.guess_type(path)

                # Assets where we may need to replace __BASE_PATH__
                text_types = {
                    "html": "text/html",
                    "css": "text/css",
                    "js": "text/javascript",
                }
                if (
                    mime_type in text_types.values()
                    or file_path.suffix in text_types.keys()
                ):
                    content = file_path.read_text(encoding="utf-8")
                    content = content.replace("__BASE_PATH__/", BASE_PATH)
                    return Response(content=content, media_type=mime_type)

                # Everything else -> read bytes and return as is
                else:
                    content = file_path.read_bytes()
                    media_type = mime_type or "application/octet-stream"
                    return Response(content=content, media_type=media_type)

            # All other paths server index.html --> hand off to Vue router
            index_path = gui_build_dir / "index.html"
            if index_path.exists():
                html_content = index_path.read_text(encoding="utf-8")
                html_content = html_content.replace("__BASE_PATH__/", BASE_PATH)
                return HTMLResponse(content=html_content)

        except Exception as err:  # pylint: disable=broad-except
            return Response(content=f"An error occurred: {err}", status_code=500)

        # Oh no
        return Response(content="index.html not found", status_code=404)

    # Determine port and host
    host, port = next_avail_port(host=config.host, port=config.port)

    # Remove logging of warning & informational messages
    log = logging.getLogger("uvicorn")
    log.setLevel(logging.ERROR)

    # Spin up the GUI API in a separate thread
    # so it doesn't block your application.
    GUI_SERVER = GUIThread(app, host, port)
    GUI_SERVER.start()

    # Wait for the server to start
    if not wait_for_port(host, port, timeout=5.0):
        raise RuntimeError("Server failed to start in time")

    # Launch the GUI
    _open_browser(host, port, path, query, hash, silent)


def _open_browser(host, port, path, query, hash, silent=False):
    # Compile the URL to be opened in the browser
    headless = "headless/" if NOTEBOOK_MODE else ""
    module_path = f"{headless}{path}" if path else headless
    url = f"http://{host}:{port}/{BASE_PATH}{module_path}{query}{hash}"

    # print("URL:", url)
    # print("BASE_PATH:", BASE_PATH)
    # print("module_path:", module_path)

    # Jupyter --> Render iframe
    if NOTEBOOK_MODE:

        # Rendering the iframe in the traditional way doesn't let
        # us style it, so we have to use a little hack, rendering
        # our iframe using HTML. Jupyter doesn't like our hack, so
        # we also have to suppress the warning.
        # The "regular" way of rendering the iframe would be:
        #
        #   from IPython.display import IFrame, display
        #   iframe = IFrame(src=f'http://{host}:{port}', width='100%', height=700)
        #   display(iframe)

        import warnings
        from IPython.display import HTML, display

        width = "100%"
        height = 700

        with warnings.catch_warnings():
            # Disable the warning about the iframe hack
            warnings.filterwarnings("ignore", category=UserWarning)

            # Styled buttons: reload & open in browser
            btn_id = "btn-wrap-" + str(round(time.time()))
            style = f"""
            <style>
                #{btn_id} {{ height:12px; right:20px; display:flex; flex-direction:row-reverse; position:relative }}
                #{btn_id} a {{ color:#393939; width:24px; height:24px; padding:4px; box-sizing:border-box; background:white }}
                #{btn_id} a:hover {{ color: #0f62fe }}
            </style>
            """
            _reload_icn = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 14C10.1867 14 11.3467 13.6481 12.3334 12.9888C13.3201 12.3295 14.0892 11.3925 14.5433 10.2961C14.9974 9.19975 15.1162 7.99335 14.8847 6.82946C14.6532 5.66558 14.0818 4.59648 13.2426 3.75736C12.4035 2.91825 11.3344 2.3468 10.1705 2.11529C9.00666 1.88378 7.80026 2.0026 6.7039 2.45673C5.60754 2.91085 4.67047 3.67989 4.01118 4.66658C3.35189 5.65328 3 6.81331 3 8V11.1L1.2 9.3L0.5 10L3.5 13L6.5 10L5.8 9.3L4 11.1V8C4 7.0111 4.29324 6.0444 4.84265 5.22215C5.39206 4.39991 6.17295 3.75904 7.08658 3.38061C8.00021 3.00217 9.00555 2.90315 9.97545 3.09608C10.9454 3.289 11.8363 3.76521 12.5355 4.46447C13.2348 5.16373 13.711 6.05465 13.9039 7.02455C14.0969 7.99446 13.9978 8.99979 13.6194 9.91342C13.241 10.8271 12.6001 11.6079 11.7779 12.1574C10.9556 12.7068 9.98891 13 9 13V14Z" fill="currentColor"/></svg>'
            _launch_icn = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13 14H3C2.73489 13.9996 2.48075 13.8942 2.29329 13.7067C2.10583 13.5193 2.00036 13.2651 2 13V3C2.00036 2.73489 2.10583 2.48075 2.29329 2.29329C2.48075 2.10583 2.73489 2.00036 3 2H8V3H3V13H13V8H14V13C13.9996 13.2651 13.8942 13.5193 13.7067 13.7067C13.5193 13.8942 13.2651 13.9996 13 14Z" fill="currentColor"/><path d="M10 1V2H13.293L9 6.293L9.707 7L14 2.707V6H15V1H10Z" fill="currentColor"/></svg>'
            _reload_btn = f"<a href=\"#\" onclick=\"event.preventDefault(); document.querySelector('#{btn_id} + iframe').src=document.querySelector('#{btn_id} + iframe').src;\">{_reload_icn}</a>"
            _launch_btn = f'<a target="_blank" href="{url.replace("/headless", "")}">{_launch_icn}</a>'
            buttons_html = f'<div id="{btn_id}">{_launch_btn}{_reload_btn}</div>'

            # Experimental fix for JupyterLab
            # - - -
            # JupyterLab renders the iframe inside a container with 20px right
            # padding, however this is not the case in Jupyter Notebook. As a
            # workaround, we force 20px extra onto the iframe width in JupyterLab
            # to counteract this padding. There's no official way to detect the
            # difference between JupyterLab and Jupyter Notebook, so this is a
            # bit of a hack. May break in future versions of Jupyter.
            is_jupyterlab = "JPY_SESSION_NAME" in os.environ
            jl_padding_correction = "width:calc(100% + 20px)" if is_jupyterlab else ""

            # Render iframe & buttons
            iframe_html = f'{style}{buttons_html}<iframe src="{url}" crossorigin="anonymous" width="{width}" height="{height}" style="border:solid 1px #ddd;box-sizing:border-box;{jl_padding_correction}"></iframe>'
            display(HTML(iframe_html))

    # CLI or python script --> Open browser
    else:
        if not silent:
            socket.setdefaulttimeout(1)
            webbrowser.open(url, new=1)

        # Display our own launch message
        _print_launch_msg(url)


def gui_shutdown(silent=False):
    """
    Shutdown the GUI server if it is running.
    """

    # Clear all working copy molsets in the /wc_cache folder
    workspace_path = ctx().workspace_path()
    cache_dir = workspace_path + "/._openad/wc_cache"
    if os.path.exists(cache_dir):
        for file in os.listdir(cache_dir):
            os.remove(os.path.join(cache_dir, file))

    # Shutdown the server
    if GUI_SERVER and GUI_SERVER.is_running():
        GUI_SERVER.shutdown()
    elif not silent:
        spf.error("The GUI server is not running")


def cleanup():
    """
    Cleanup function to be called at exit of the main process.
    """
    gui_shutdown(silent=True)


# Stylized launch message for the web server
def _print_launch_msg(url):
    spf(f"<yellow>Launching GUI:</yellow>\n<link>{url}</link>", pad=1)


# Stylized shutdown message for the web server
def _print_shutdown_msg(host, port):
    # prefix_char = "&empty;"
    # prefix = f"<red>{html.unescape(prefix_char)}</red> "
    prefix = "🚫 "
    spf.success(
        [
            f"{prefix}OpenAD GUI shutdown complete",
            f"{prefix}{host}:{port}",
        ],
        pad=1,
    )


atexit.register(cleanup)
