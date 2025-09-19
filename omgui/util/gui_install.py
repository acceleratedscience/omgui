"""
Install the GUI build files if they are not already installed.
"""

import os
import tarfile
import urllib.request
from pathlib import Path
from spf import spf


def ensure():
    """
    Check if the GUI build files are installed, and install them if not.
    """

    # Root directory of the repo
    app_dir = Path(__file__).resolve().parents[1]

    if not os.path.exists(app_dir / "dist"):
        install(app_dir)


def install(destination_dir: Path, v: str = "0.2"):
    """
    Download and install the GUI build files.
    """
    spf("<soft>Installing GUI...</soft>")

    download_url = f"https://github.com/acceleratedscience/openad-gui/releases/download/v{v}/dist.tar.gz"

    # Download the tarball
    tarball_path = os.path.join(destination_dir, "dist.tar.gz")
    urllib.request.urlretrieve(download_url, tarball_path)

    # Unzip & remove the tarball
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=destination_dir)

    os.remove(tarball_path)
