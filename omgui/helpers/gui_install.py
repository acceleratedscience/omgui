"""
Install the GUI build files if they are not already installed.
"""

import os
import tarfile
import urllib.request
from pathlib import Path
from openad.helpers.output import output_text


def ensure():
    """
    Check if the GUI build files are installed, and install them if not.
    """

    # Root directory of the repo
    root_dir = Path(__file__).resolve().parents[2]

    if not os.path.exists(root_dir / "gui-build"):
        install(root_dir)


def install(destination_dir: Path, v: str = "0.2"):
    """
    Download and install the GUI build files.
    """
    output_text("<soft>Installing GUI...</soft>", return_val=False)

    download_url = f"https://github.com/acceleratedscience/openad-gui/releases/download/v{v}/gui-build.tar.gz"

    # Download the tarball
    tarball_path = os.path.join(destination_dir, "gui-build.tar.gz")
    urllib.request.urlretrieve(download_url, tarball_path)

    # Unzip & remove the tarball
    with tarfile.open(tarball_path, "r:gz") as tar:
        tar.extractall(path=destination_dir)

    os.remove(tarball_path)
