import os


# Temporary singleton class to mimic cmd_pointer
# This will be replaced by a config file or similar in the future


class CmdPointerTemp:
    api_variables = {}
    settings = {"workspace": "DEFAULT", "workspaces": ["DEFAULT"]}
    molecule_list = []
    last_external_molecule = None

    def workspace_path(self, workspace_name=None):
        return os.path.expanduser("~/.openad/workspaces/DEFAULT")


# Singleton instance
cmd_pointer = CmdPointerTemp()
