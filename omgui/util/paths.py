# Std
import os
import re
from pathlib import Path

# OMGUI
from omgui import ctx
from omgui.util.general import confirm_prompt
from omgui.spf import spf


NOT_ALLOWED_ERR = [
    "Absolute paths are not allowed here",
    "To import this file into your workspace, run <cmd>import '{file_path}'</cmd>",
]


def prepare_file_path(file_path: Path | str, fallback_ext=None, force_ext=None):
    """
    prepare a file path for saving.

    - Parse the path and turn into absolute path
    - Check if there is already a file at this location
        - If yes, ask to overwrite:
            - if yes, return the file path
            - if no, return the file path with the next available filename
        - If no, check if the folder structure exists
            - if yes, return the file path
            - if no, ask to create the folder structure
                - if yes, return the file path
                - if no, print error and return None
    """
    file_path = Path(file_path)
    file_path = parse_path(file_path, fallback_ext, force_ext)
    file_path = _ensure_file_path(file_path)
    # if not file_path:
    #     spf.error("Directory does not exist")
    #     return None
    return file_path


def parse_path(
    file_path: Path | str,
    fallback_ext: str = None,
    force_ext: str = None,
) -> str:
    """
    Parse a path string to a path object.

    - foo:  workspace path
    - /foo: absolute path
    """

    if not file_path:
        return None

    file_path = Path(file_path)

    # Detect path type
    is_absolute = file_path.is_absolute()
    is_cwd = file_path.parts[0] in (".", "..")

    # Expand user path: ~/... --> /Users/my-username/...
    file_path = file_path.expanduser()

    # Separate filename from path
    path = file_path.parent
    filename = file_path.name

    # Force extension
    new_ext = None
    if force_ext:
        stem = file_path.stem
        ext = file_path.suffix
        filename = stem + "." + force_ext
        if ext and ext[1:] != force_ext:
            new_ext = force_ext

    # Fallback to default extension if none provided
    elif fallback_ext:
        ext = file_path.suffix
        filename = filename if ext else filename + "." + fallback_ext

    # Absolute path
    if is_absolute:
        # TODO: used to be jup_is_proxy, need to figure out what
        # to do with file paths in proxy, maybe this shoudl be
        # blocked with dedicated env bar instead.
        # if is_proxy():
        #     spf.error(NOT_ALLOWED_ERR)
        #     return None
        path = path / filename

    # Current working directory path
    elif is_cwd:
        path = Path.cwd() / path / filename

    # Default: workspace path
    else:
        path = ctx().workspace_path() / path / filename

    # Display wrning when file extension is changed
    if new_ext:
        spf.warning(
            [
                f"⚠️  File extension changed to <reset>{new_ext}</reset>",
                f"--> {path if is_absolute else filename}",
            ]
        )
    return path


def _ensure_file_path(file_path: Path, force: bool = False) -> bool:
    """
    Ensure a file_path is valid.

    - Make sure we won't override an existing file
    - Create folder structure if it doesn't exist yet
    """
    if file_path.exists():
        # File already exists --> overwrite?
        if not force and not confirm_prompt(
            "The destination file already exists, overwrite?"
        ):
            return _next_available_filename(file_path)
    elif not file_path.parent.exists():
        # Directory doesn't exist --> create?
        if not force and confirm_prompt(
            "The destination directory does not exist, create it?"
        ):
            return False
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as err:
            spf.error(["Error creating directory", err])
            return False
    return file_path


def _next_available_filename(file_path: Path) -> str:
    """
    Returns the file path with next available filename by appending a number to the filename.
    """
    if not file_path.exists():
        return file_path

    stem = None
    ext = None
    if file_path.lower().endswith(".mol.json"):
        stem = re.sub(r"(\.mol\.json)$", "", file_path)
        ext = ".mol.json"
    elif file_path.lower().endswith(".smol.json"):
        stem = re.sub(r"(\.smol\.json)$", "", file_path)
        ext = ".smol.json"
    elif file_path.lower().endswith(".mmol.json"):
        stem = re.sub(r"(\.mmol\.json)$", "", file_path)
        ext = ".mmol.json"
    elif file_path.lower().endswith(".molset.json"):
        stem = re.sub(r"(\.molset\.json)$", "", file_path)
        ext = ".molset.json"
    else:
        stem = file_path.stem
        ext = file_path.suffix

    i = 1
    while Path(f"{stem}-{i}{ext}").exists():
        i += 1
    return f"{stem}-{i}{ext}"


def block_absolute(file_path) -> bool:
    """
    Display error when absolute paths are not allowed.

    Usage:
    if block_absolute(file_path):
        return
    """
    if is_abs_path(file_path):
        spf.error(NOT_ALLOWED_ERR)
        return True
    return False


def is_abs_path(file_path) -> bool:
    """
    Check if a path is absolute.
    """
    if file_path.startswith(("/", "./", "~/", "\\", ".\\", "~\\")):
        return True
    return False


def fs_success(
    path_input,  # Destination user input, eg. foo.csv or /home/foo.csv or ./foo.csv
    path_resolved,  # Destination parsed through parse_path, eg. /home/user/foo.csv
    subject="File",
    action="saved",  # saved / removed
):
    """
    Path-type aware success message for saving files.
    """
    # Absolute path
    if is_abs_path(path_input):
        spf.success(f"{subject} {action}: <yellow>{path_resolved}</yellow>")

    # Workspace path
    else:
        # Filename may have been modifier with index and extension,
        # so we need to parse it from the file_path instead.
        workspace_path = ctx().workspace_path()
        within_workspace_path = path_resolved.replace(workspace_path, "").lstrip("/")
        if action == "saved":
            spf.success(
                f"{subject} saved to workspace as <yellow>{within_workspace_path}</yellow>"
            )
        elif action == "removed":
            spf.success([f"{subject} removed from workspace", within_workspace_path])
