"""
This file contains the GUI launcher and installer.

The GUI is launched in a separate thread using werkzeug via ServerThread.
The launcher will either start up the GUI server, or open the GUI in a
browser if the server was already active.
"""

import os
import json
import time
import html
import socket
import atexit
import uvicorn
import logging
import mimetypes
import webbrowser
import urllib.parse
from time import sleep
from pathlib import Path
from threading import Thread
from cmd_pointer import cmd_pointer

# FastAPI
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse


from openad.helpers.output import (
    output_text,
    output_error,
    output_success,
    output_warning,
)

from openad.app.global_var_lib import GLOBAL_SETTINGS


import gui_routes
from helpers import gui_install
from helpers.general import next_avail_port
from helpers.exception_handlers import register_exception_handlers


GUI_SERVER = None

# Optional BASE_PATH environment variable
# We always want it w/o leading slash, but with trailing slash
# See proxy_server.py for details
BASE_PATH = (
    (os.environ.get("BASE_PATH", "").strip("/") + "/")
    if os.environ.get("BASE_PATH")
    else ""
)


def gui_init(cmd_pointer=None, path=None, data=None, silent=False):
    """
    Check if the GUI is installed and start the server.

    If this GUI is not installed (openad-gui folder not present),
    suggest to install it, unless the user has chosen before not
    to be asked again (openad-gui folder present without index.html).

    Parameters
    ----------
    cmd_pointer : object, required
        The command pointer object.
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

    # Install the GUI if needed
    gui_install.ensure()

    # Parse potential data into a URL string.
    query = "?data=" + urllib.parse.quote(json.dumps(data)) if data else ""

    # Launch the GUI.
    _launch(cmd_pointer=cmd_pointer, path=path, query=query, silent=silent)


def _launch(cmd_pointer=None, path=None, query="", hash="", silent=False):
    """
    Launch the GUI web server in a separate thread.
    """

    global GUI_SERVER

    # If the server is already running, don't launch it again
    if GUI_SERVER and GUI_SERVER.is_running():
        _open_browser(GUI_SERVER.host, GUI_SERVER.port, path, query, hash, silent)
        return

    # Initialize Flask app
    gui_build_dir = Path(__file__).resolve().parents[1] / "gui-build"

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
    gui_router = gui_routes.create_router(cmd_pointer)
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
        return "OpenAD GUI shutdown complete"

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

            # Check is the requested path is a static asset
            # and serve it with the BASE_PATH replaced.
            if path != "" and (gui_build_dir / path).exists():
                content = (gui_build_dir / path).read_text(encoding="utf-8")
                content = content.replace("__BASE_PATH__/", BASE_PATH)
                mime_type, _ = mimetypes.guess_type(path)
                return Response(content=content, media_type=mime_type)

            # All other paths server index.html --> hand off to Vue router
            index_path = gui_build_dir / "index.html"
            if index_path.exists():
                html_content = index_path.read_text(encoding="utf-8")
                html_content = html_content.replace("__BASE_PATH__/", BASE_PATH)
                return HTMLResponse(content=html_content)

        except Exception as e:  # pylint: disable=broad-except
            return Response(content=f"An error occurred: {e}", status_code=500)

        # Oh no
        return Response(content="index.html not found", status_code=404)

    # Determine port and host
    host, port = next_avail_port()

    # Launch the UI
    _open_browser(host, port, path, query, hash, silent)

    # Remove logging of warning & informational messages
    log = logging.getLogger("uvicorn")
    log.setLevel(logging.ERROR)

    # We need to spin up the OMGUI server in a separate
    # thread, otherwise it would be blocking the application.
    #
    # Hence, we can't do:
    #   app.run(host=host, port=port)
    #
    # To spin it up in a separate thread, we could do:
    #   THREAD = Thread(target=lambda: app.run(host=host, port=port))
    #
    # But unfortunately Flask's built-in server doesn't provide an option
    # to shut it down programatically from another thread, so instead
    # we use Werkzeug's more advanced WSGI server.
    GUI_SERVER = ServerThread(app, host, port)
    GUI_SERVER.start()

    # IMPORTANT
    # Pause long enough for the flask server to start
    # Issue can be that jupyter has race condition for resources and the server does not start.
    # On first starting Server says it is alive but there must be some resource contention that sees it close shorlty after starting
    # is_alive and -s_running both return ok so need to enformce mandatory pause to ensure no abend
    sleep(0.5)


# This class replaces Flask's builtin app.run() server,
# and allows us to shut down the server from another thread.
# - - -
# In practice, this happens on KeyboardInterrupt in cmd_line().
# See GUI_SERVER.shutdown() in main.py.
class ServerThread(Thread):
    def __init__(self, app, host, port):
        Thread.__init__(self)
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
        return self.active

    def shutdown(self):
        if self.server:
            self.server.should_exit = True
        self.join()
        self.active = False
        prefix = f"<red>{html.unescape('&empty;')}</red> "
        output_success(
            [
                f"{prefix}OpenAD GUI shutdown complete",
                f"{prefix}{self.host}:{self.port}",
            ]
        )


def _open_browser(host, port, path, query, hash, silent=False):
    headless = "headless" if GLOBAL_SETTINGS["display"] == "notebook" else ""
    module_path = f"{headless}/{path}" if path else ""

    # Jupyter --> Render iframe.
    if GLOBAL_SETTINGS["display"] == "notebook":
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
            # Disable the warning about the iframe hack.
            warnings.filterwarnings("ignore", category=UserWarning)

            # Styled buttons: reload & open in browser.
            id = "btn-wrap-" + str(round(time.time()))
            style = f"""
            <style>
                #{id} {{ height:12px; right:20px; display:flex; flex-direction:row-reverse; position:relative }}
                #{id} a {{ color:#393939; width:24px; height:24px; padding:4px; box-sizing:border-box; background:white }}
                #{id} a:hover {{ color: #0f62fe }}
            </style>
            """

            url = f"http://{host}:{port}/{BASE_PATH}{module_path}{query}{hash}"

            reload_icn = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 14C10.1867 14 11.3467 13.6481 12.3334 12.9888C13.3201 12.3295 14.0892 11.3925 14.5433 10.2961C14.9974 9.19975 15.1162 7.99335 14.8847 6.82946C14.6532 5.66558 14.0818 4.59648 13.2426 3.75736C12.4035 2.91825 11.3344 2.3468 10.1705 2.11529C9.00666 1.88378 7.80026 2.0026 6.7039 2.45673C5.60754 2.91085 4.67047 3.67989 4.01118 4.66658C3.35189 5.65328 3 6.81331 3 8V11.1L1.2 9.3L0.5 10L3.5 13L6.5 10L5.8 9.3L4 11.1V8C4 7.0111 4.29324 6.0444 4.84265 5.22215C5.39206 4.39991 6.17295 3.75904 7.08658 3.38061C8.00021 3.00217 9.00555 2.90315 9.97545 3.09608C10.9454 3.289 11.8363 3.76521 12.5355 4.46447C13.2348 5.16373 13.711 6.05465 13.9039 7.02455C14.0969 7.99446 13.9978 8.99979 13.6194 9.91342C13.241 10.8271 12.6001 11.6079 11.7779 12.1574C10.9556 12.7068 9.98891 13 9 13V14Z" fill="currentColor"/></svg>'
            launch_icn = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13 14H3C2.73489 13.9996 2.48075 13.8942 2.29329 13.7067C2.10583 13.5193 2.00036 13.2651 2 13V3C2.00036 2.73489 2.10583 2.48075 2.29329 2.29329C2.48075 2.10583 2.73489 2.00036 3 2H8V3H3V13H13V8H14V13C13.9996 13.2651 13.8942 13.5193 13.7067 13.7067C13.5193 13.8942 13.2651 13.9996 13 14Z" fill="currentColor"/><path d="M10 1V2H13.293L9 6.293L9.707 7L14 2.707V6H15V1H10Z" fill="currentColor"/></svg>'
            reload_btn = f"<a href=\"#\" onclick=\"event.preventDefault(); document.querySelector('#{id} + iframe').src=document.querySelector('#{id} + iframe').src;\">{reload_icn}</a>"
            launch_btn = f'<a target="_blank" href="{url.replace("/headless", "")}">{launch_icn}</a>'
            btn_wrap = f'<div id="{id}">{launch_btn}{reload_btn}</div>'

            # Experimental fix for JupyterLab.
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

            iframe_html = f'{style}{btn_wrap}<iframe src="{url}" crossorigin="anonymous" width="{width}" height="{height}" style="border:solid 1px #ddd;box-sizing:border-box;{jl_padding_correction}"></iframe>'
            display(HTML(iframe_html))

    # CLI --> Open browser.
    else:
        url = f"http://{host}:{port}{module_path}{query}{hash}"
        if not silent:
            socket.setdefaulttimeout(1)
            webbrowser.open(url, new=1)

        # Display our own launch message.
        _print_launch_msg(url)


# Generated a stylized launch message for the web server.
def _print_launch_msg(url):
    output_text(f"<yellow>Launching GUI:</yellow>\n<link>{url}</link>", pad=1)


# Generated a stylized launch message for the web server
# – no longer useful since we don't launch it on startup
def _print_launch_msg_TRASH(host, port):
    text = "User interface:"
    url = f"{host}:{port}"
    width = max(len(text), len(url))
    edge = width * "-"
    launch_msg = [
        f"+ {edge} +",
        f"| <yellow>{text}{(width - len(text)) * ' '}</yellow> |",
        f"| <link>{url}</link>{(width - len(url)) * ' '} |",
        f"+ {edge} +",
    ]
    launch_msg = "\n".join(launch_msg)

    # Print
    output_text(launch_msg, pad=1, tabs=1)


# Shutdown the GUI server.
def gui_shutdown(cmd_pointer=None, ignore_warning=False):
    # Clear all working copy molsets in the /wc_cache folder

    if cmd_pointer is not None:
        workspace_path = cmd_pointer.workspace_path(cmd_pointer.settings["workspace"])

        cache_dir = workspace_path + "/._openad/wc_cache"

        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                os.remove(os.path.join(cache_dir, file))

    if GUI_SERVER and GUI_SERVER.is_running():
        GUI_SERVER.shutdown()
    elif not ignore_warning:
        output_error("The GUI server is not running")
        return


def cleanup():
    gui_shutdown(ignore_warning=True)


atexit.register(cleanup)

if __name__ == "__main__":
    gui_init(cmd_pointer)
