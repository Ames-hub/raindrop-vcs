from library.storage import var, dt
import shutil
import os

class versionControlSystem:
    def __init__(self, username=None, repo_id="*", token=None):
        """
        A class to manage versions of your code.

        Records all changes to all files and has the ability to revert any file to any previous version.
        :param repo_id:
        """
        if token is None and username is not None:
            self.username = username
            self.allow_secured_services = False
        else:
            # Does not check token validity. Userman does that.
            self.token = token
            # If token is provided, allow secured services. This means the user is logged in.
            self.allow_secured_services = True

        self.repo_id = repo_id
        self.root_dir = os.path.abspath(os.path.join('data', 'users', str(username), 'repositories', str(repo_id)))
        self.repo_main_dir = os.path.join(self.root_dir, 'branches', 'main')
        self.repo_config = os.path.join(self.repo_main_dir, '.rdvcs')
        self.is_initialized = self.exists()
        self.is_owner = var.get('owner', file=self.repo_config) == self.username
        if self.is_initialized:
            self.version = self.get_version()  # Gets the highest version released.

    def exists(self):
        """
        Checks if the repository exists.
        """
        return os.path.exists(self.repo_config)

    def walk(self, version='latest') -> dict | bool:
        """
        Walks through the repository and returns the directories and files.
        """
        if version == 'latest':
            version = self.version

        directories = {}
        version_dir = os.path.join(self.root_dir, version)

        if not os.path.exists(version_dir):
            return False

        for root, dirs, files in os.walk(version_dir):
            directories[root] = files

        return directories

    def get_version(self):
        # Reads the .rdvcs file and returns the version.
        return var.get('version', file=self.repo_config)

    def init_repo(self, description: str = None):
        """
        Initializes a new repository.
        """
        os.makedirs(self.repo_main_dir, exist_ok=True)

        repo_conf = dt.REPO_CONFIG
        repo_conf['name'] = self.repo_id
        repo_conf['description'] = description
        # Reminder, 1.0.0 = Major.Minor.Patch. Major here, includes release or 'ver 1'.
        repo_conf['version'] = [1, 0, 0]
        repo_conf['owner'] = self.username

        var.fill_json(os.path.join(self.repo_config, repo_conf))

    def push(self, file: bytes, rel_dir: str, update_cat='patch') -> bool:
        """
        Pushes a file to the repository.
        :param file: The file as bytes data to push.
        :param rel_dir: The relative directory to the file.
        :param update_cat: The category of the update. (major, minor, patch)
        """
        assert update_cat in ['major', 'minor', 'patch'], 'Invalid update category.'
        assert file is not None, 'File is empty.'
        assert type(file) is bytes, 'File must be bytes data.'
        assert rel_dir is not None, 'Relative directory is empty.'

        # Create a snapshot of the file before writing to it.
        self.new_snapshot()

        file_dir = os.path.join(self.repo_main_dir, rel_dir)
        os.makedirs(file_dir, exist_ok=True)
        # In the main branch, write the new version file.
        var.set('version', self.version, file=self.repo_config)

        with open(file_dir, 'wb') as f:
            f.write(file)

        return True

    def pull(self, rel_dir, version) -> bytes | None:
        """
        Pulls a file from the repository.
        :param version:
        :param rel_dir: The relative directory to the file.
        :return: The file as bytes data.
        """
        assert type(rel_dir) is str, 'Relative directory must be a string.'
        assert type(version) is list
        # Enforces the format of list [major, minor, patch]
        assert len(version) == 3, 'Version must be in the format [major, minor, patch].'
        if not os.path.exists(os.path.join(self.root_dir, version)):
            return None

        file_dir = os.path.join(self.root_dir, version, rel_dir)

        with open(file_dir, 'rb') as f:
            return f.read()

    def new_snapshot(self):
        """
        Creates a new snapshot of the repository.
        """
        snapshot_dir = os.path.join(self.root_dir, 'snapshots')
        os.makedirs(snapshot_dir, exist_ok=True)

        snapshot_dir = os.path.join(snapshot_dir, self.version)
        shutil.copytree(self.root_dir, snapshot_dir)
