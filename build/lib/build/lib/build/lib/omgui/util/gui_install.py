"""
Install the GUI build files if they are not already installed.
"""

import os
import tarfile
import urllib.request
from pathlib import Path
from omgui.spf import spf


def ensure():
    """
    Check if the GUI build files are installed, and install them if not.
    """
    # Root directory of the repo
    app_dir = Path(__file__).resolve().parents[1]

    if not os.path.exists(app_dir / "gui" / "client"):
        destination_dir = app_dir / "gui"
        install(destination_dir)


def install(destination_dir: Path, v: str = "0.2"):
    """
    Download and install the GUI build files.
    """
    print(444, destination_dir)
    spf("<soft>Installing GUI...</soft>", pad_top=1)

    download_url = f"https://github.com/acceleratedscience/openad-gui/releases/download/v{v}/dist.tar.gz"

    # Download the tarball
    tarball_path = Path(destination_dir) / "dist.tar.gz"
    urllib.request.urlretrieve(download_url, tarball_path)

    # Unzip the tarball
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=destination_dir)

    # Rename "dist" to "client"
    os.rename(destination_dir / "dist", destination_dir / "client")

    # Remove the tarball
    os.remove(tarball_path)

    spf.success("<soft>Installation complete</soft>")
