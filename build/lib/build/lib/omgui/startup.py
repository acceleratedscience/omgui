# Std
from time import sleep
from threading import Thread
from pathlib import Path

# OMGUI
from omgui.context import ctx
from omgui.configuration import config


def startup():
    """
    Application startup routine.
    """

    # Note: the ._system dir and mws.json file are created by ctx._load_mws()

    def _startup():
        # Wait for configure() to have been applied
        sleep(0.1)

        # Create workspace if not existing
        workspace = config().workspace
        workspace_path = ctx().workspace_path()
        if not workspace_path.exists():
            ctx().create_workspace(workspace)

            # Add sample files to workspace
            if config().sample_files:
                _load_sample_files()

        # Set workspace
        else:
            ctx().set_workspace(workspace, silent=True)

        # Add sample files to workspace
        if config().sample_files:
            _load_sample_files()

    Thread(target=_startup).start()


def _load_sample_files():
    """
    Load sample files into the current workspace.
    """
    import tarfile

    sample_file = Path(__file__).parent / "gui" / "data" / "samples.tar.gz"
    workspace_path = ctx().workspace_path()

    with tarfile.open(sample_file, "r:gz") as tar_ref:
        tar_ref.extractall(workspace_path)
