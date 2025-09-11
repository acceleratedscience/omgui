import os
from workers.file_system import (
    fs_get_workspace_files,
    fs_attach_file_data,
    fs_compile_filedir_obj,
)
from openad.helpers.output import output_success


class FileSystemApi:
    """
    API endpoints related to the file system.
    """

    def __init__(self, cmd_pointer):
        self.cmd_pointer = cmd_pointer

    def get_workspaces(self):
        """
        Fetch list of workspaces.
        """
        return {
            "all": self.cmd_pointer.settings["workspaces"],
            "active": self.cmd_pointer.settings["workspace"],
        }

    def get_workspace(self):
        """
        Fetch the name of the active workspace.
        """
        return self.cmd_pointer.settings["workspace"]

    def set_workspace(self, workspace_name):
        """
        Set the active workspace.
        """
        current_workspace_name = self.cmd_pointer.settings["workspace"]
        workspace_diff = workspace_name != current_workspace_name
        workspace_exists = workspace_name in self.cmd_pointer.settings["workspaces"]
        if workspace_exists and workspace_diff:
            self.cmd_pointer.settings["workspace"] = workspace_name
            self.cmd_pointer.histfile = os.path.expanduser(
                self.cmd_pointer.workspace_path(workspace_name) + "/.cmd_history"
            )
            output_success(f"Workspace set to <yellow>{workspace_name}</yellow>")

        return "ok"

    def get_workspace_files(self, path=""):
        """
        Fetch your active workspace's content as a JSON object.
        """
        return fs_get_workspace_files(self.cmd_pointer, path)

    def get_file(self, path="", query=None):
        """
        Fetch a file's content as a JSON object.
        """
        if not query:
            query = {}

        # Compile filedir object
        file_obj = fs_compile_filedir_obj(self.cmd_pointer, path)
        file_type = file_obj.get("_meta", {}).get("fileType")

        # Attach data for files
        if file_type and file_type != "dir":
            file_obj = fs_attach_file_data(self.cmd_pointer, file_obj, query)

        return file_obj

    def open_file_os(self, path_absolute=""):
        """
        Open a file in its designated OS application.
        """
        try:
            os.system(f"open '{path_absolute}'")
            return "ok", 200
        except OSError as err:
            return err, 500

    def delete_file(self, path_absolute=""):
        """
        Move a file to the workspace trash.
        The trash gets cleared at the end of a session.
        """
        trash_dir = f"{self.cmd_pointer.workspace_path()}/.trash"
        os.makedirs(trash_dir, exist_ok=True)
        os.system(f"mv '{path_absolute}' '{trash_dir}'")

        return "ok", 200
