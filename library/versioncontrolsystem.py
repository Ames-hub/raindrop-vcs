from library.cmd_interface import cli_handler
from library.storage import PostgreSQL
from library.user_login import users
from library.errors import error
import datetime
import shutil
import uuid
import git
import os

def greet_func():
    print("Welcome to the Raindrop Versioning System CLI.")
    print("Logged in as Raindrop. Type 'version' to start versioning a repository.")
    print("Type 'help' for a list of commands.")
    return True

versioning_cli = cli_handler(
    cli_name="versioning",
    greet_func=greet_func,
    is_main_cli=False,
    use_plugins=False
)

class vmsystem:
    """
    Version Memory/Management System for a repository.
    """
    def __init__(self, owner, repo_uuid4):
        self.db = PostgreSQL()
        self.owner = owner
        self.repo_uuid4 = repo_uuid4
        rd_config().exists(owner, repo_uuid4)

    @staticmethod
    def cli():
        versioning_cli.register_command(
            cmd='version',
            description="Add a new version to a repository.",
            func=vmsystem.cli_funcs.version,
        )

        versioning_cli.main()
        return True

    def increment_version(self, amount_lines_changed:int=None, ver_type:str=None):
        """
        Add a new version to the repository.
        It does this by tracking MAJOR, MINOR, and PATCH versions.

        MAJOR: The major version is incremented when the repository is significantly changed. (1000+ lines changed)
        MINOR: The minor version is incremented when the repository is moderately changed. (100-999 lines changed)
        PATCH: The patch version increments when the repository gets slightly changed. (1-99 lines changed)

        :param amount_lines_changed: The number of lines of code changed in this version. If None, uses ver_type arg.
        :param ver_type: The type of version change. If None, uses lines_changed arg.
        :return: True if successful, False if not
        """
        # Get the current version
        repo_name = self.db.get_repo_name_via_uuid4_repo_crossref(self.repo_uuid4)
        rdc = rd_config().read(self.owner, repo_name)
        version = [int(rdc['v_major']), int(rdc['v_minor']), int(rdc['v_patch'])]

        if amount_lines_changed is not None:
            # Extrapolate the release type
            ver_type = self.extrapolate_RDrt(amount_lines_changed)
        else:
            # Check if the version type is valid
            if not type(ver_type) is str:
                raise error.InvalidVersionType(f"Version type \"{ver_type}\" is not a string. Got type: {type(ver_type)}")
            if ver_type not in ['MAJOR', 'MINOR', 'PATCH']:
                raise error.InvalidVersionType(f"Invalid version type: {ver_type}")

            # Put it in a dictionary to match the extrapolate_RDrt function
            ver_type = {'type': ver_type, 'inttype': 1 if ver_type == 'MAJOR' else 2 if ver_type == 'MINOR' else 3}

        # Increment the version
        if ver_type['inttype'] == 1:
            version[0] += 1
            version[1] = 0
            version[2] = 0
        elif ver_type['inttype'] == 2:
            version[1] += 1
            version[2] = 0
        elif ver_type['inttype'] == 3:
            version[2] += 1
        else:
            raise error.InvalidVersionType(f"Invalid version type: {ver_type['inttype']}")

        # Update the version in the RDC file
        rd_config().update('v_major', version[0], repo_name, self.owner)
        rd_config().update('v_minor', version[1], repo_name, self.owner)
        rd_config().update('v_patch', version[2], repo_name, self.owner)

        return True

    @staticmethod
    def extrapolate_RDrt(lines_changed) -> dict:
        """
        Extrapolate the Raindrop versioning release type based on the number of lines changed.
        :param lines_changed: The number of lines changed
        :return: The release type
        """
        if lines_changed > 700:
            return {'type': 'MAJOR', 'inttype': 1}
        elif 100 <= lines_changed <= 700:
            return {'type': 'MINOR', 'inttype': 2}
        else:
            return {'type': 'PATCH', 'inttype': 3}

    class cli_funcs:
        @staticmethod
        def version():
            try:
                owner, repo_name = versioning_cli.ask_question(
                    question="Enter \"Owner/Repository\" to select the repository to version.",
                    default="exit",
                    show_default=False,
                    exit_phrase="exit",
                    confirm_validity=True,
                    filter_func=lambda x: len(x.split('/')) == 2,
                    filter_func_fail_msg="Repository not found.",
                ).split('/')
                exists = VCS.repository_exists(owner, repo_name)
                if not exists:
                    print("Repository not found.")
                    return True
                print(f"Repository '{repo_name}' of {owner} found.")
            except cli_handler.exited_questioning:
                print("Cancelled.")
                return True

            ver_type = versioning_cli.ask_question(
                question="What release type is this? (MAJOR, MINOR, PATCH)",
                options=['MAJOR', 'MINOR', 'PATCH'],
                default="MINOR",
            )
            if ver_type is None:
                return False

            repo_uuid4 = PostgreSQL().get_repo_uuid4_via_repo_name_crossref(repo_name)

            vmsystem(owner=owner, repo_uuid4=repo_uuid4).increment_version(ver_type=ver_type)
            print("Version added.")
            return True

class rd_config:
    def __init__(self):
        self.rdc_file = None

    def exists(self, owner, repo_name=None, repo_uuid4=None) -> bool:
        if repo_uuid4 is not None and repo_name is None:
            # Get the repo name from the database
            repo_name = PostgreSQL().get_repo_name_via_uuid4_repo_crossref()

        self.rdc_file = f'data/vcs/{owner}/repositories/{repo_name}/.rdc'
        return os.path.exists(self.rdc_file)

    def read(self, owner, repo_name) -> dict:
        """
        Read the RDC file for a repository.

        :param owner:
        :param repo_name:
        :return:
        """
        self.rdc_file = f'data/vcs/{owner}/repositories/{repo_name}/.rdc'
        with open(self.rdc_file, 'r') as f:
            data = f.read()

        # Parse the data
        line_list = data.split('\n')
        rdc_dict = {}
        for line in line_list:
            if len(line) <= 0:
                continue
            try:
                key, value = line.split("=", maxsplit=1)
            except ValueError:
                print(f"Error parsing line in RDC read func: {line}")
                continue

            # Parse back the description
            rdc_dict[key] = value.replace("<br>", "\n")

        return rdc_dict

    def write(self, repo_owner, repo_name, description, visibility) -> uuid.UUID:
        """
        Write a new RDC file for a repository.
        This function will also add the UUID to the PostgreSQL database.
        This is not to be used for updating an existing RDC file.

        :param repo_owner:
        :param repo_name:
        :param description:
        :param visibility:
        :return:
        """
        if not visibility in ['private', 'public', 'unlisted']:
            raise error.InvalidRepoVisibility(f"Invalid visibility {visibility}")

        if self.rdc_file is None:
            self.rdc_file = f'data/vcs/{repo_owner}/repositories/{repo_name}/.rdc'

        if os.path.exists(self.rdc_file):
            raise error.RDC_AlreadyExists(f"RDC already exists for {repo_name}")

        # Parse the description to allow for any/all problematic characters.
        description = description.replace("\n", "<br>")

        UUID = uuid.uuid4()
        PostgreSQL().add_uuid4_repo_crossref(repo_owner, UUID)

        try:
            with open(self.rdc_file, 'w') as f:
                f.write(f"owner={repo_owner}\n")
                f.write(f"name={repo_name}\n")
                f.write(f"description={description}\n")
                f.write(f"uuid={UUID}\n")
                f.write(f"visibility={visibility}\n")
                f.write(f"created_at={datetime.datetime.now()}\n")
                f.write(f"last_update_at={datetime.datetime.now()}\n")
                f.write(f"v_major=0\n")
                f.write(f"v_minor=0\n")
                f.write(f"v_patch=0\n")
        except Exception as e:
            raise error.RDCWriteError(f"Failed to write to RDC: {e}")

        return UUID

    def update(self, key, value, repo_name, repo_owner):
        """
        Update a key in the RDC file.

        :param key: The key to update
        :param value: The value to update the key to
        :param repo_name: The name of the repository
        :param repo_owner: The owner of the repository
        :return:
        """
        if self.rdc_file is None:
            self.rdc_file = f'data/vcs/{repo_owner}/repositories/{repo_name}/.rdc'

        if not os.path.exists(self.rdc_file):
            raise error.RDCNotFound(f"RDC not found for {repo_name}")

        with open(self.rdc_file, 'r') as f:
            data = f.read()

        # Parse the data
        line_list = data.split('\n')
        rdc_dict = {}
        for line in line_list:
            if len(line) <= 0:
                continue
            try:
                k, v = line.split("=", maxsplit=1)
            except ValueError:
                print(f"Error parsing in RDC update func. Line: {line}")
                continue
            rdc_dict[k] = v

        rdc_dict[key] = value

        try:
            with open(self.rdc_file, 'w') as f:
                f.write(f"owner={rdc_dict['owner']}\n")
                f.write(f"name={rdc_dict['name']}\n")
                f.write(f"description={rdc_dict['description']}\n")
                f.write(f"uuid={rdc_dict['uuid']}\n")
                f.write(f"visibility={rdc_dict['visibility']}\n")
                f.write(f"created_at={rdc_dict['created_at']}\n")
                f.write(f"last_update_at={datetime.datetime.now()}\n")
                f.write(f"v_major={rdc_dict['v_major']}\n")
                f.write(f"v_minor={rdc_dict['v_minor']}\n")
                f.write(f"v_patch={rdc_dict['v_patch']}\n")
        except Exception as e:
            raise error.RDCWriteError(f"Failed to write to RDC: {e}")

        return True

class VCS:
    def __init__(self, owner, repo_name):
        self.repo_path = f'data/vcs/{owner}/repositories/{repo_name}'
        self.owner = owner
        self.repo_name = repo_name

        if not os.path.exists(self.repo_path):
            raise error.RepositoryNotFound(f"Repository {repo_name} not found for {owner}")

        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise error.InvalidRepositoryError(f"Invalid Git repository at {self.repo_path}")

    @staticmethod
    def list_public_repositories(owner):
        repos_dir = f'data/vcs/{owner}/repositories/'
        if not os.path.exists(repos_dir):
            return []
        return [repo for repo in os.listdir(repos_dir) if os.path.isdir(os.path.join(repos_dir, repo))]

    @staticmethod
    def repository_exists(owner, repo_name):
        return os.path.exists(f'data/vcs/{owner}/repositories/{repo_name}/.rdc')

    @staticmethod
    def create_repository(owner, repo_name, description='', visibility='private') -> uuid.UUID:
        repo_path = f'data/vcs/{owner}/repositories/{repo_name}'
        if os.path.exists(repo_path):
            raise error.RepositoryAlreadyExists(f"Repository {repo_name} already exists for {owner}")
        os.makedirs(repo_path, exist_ok=True)
        git.Repo.init(repo_path)

        UUID4 = rd_config().write(
            repo_owner=owner,
            repo_name=repo_name,
            description=description,
            visibility=visibility,
        )

        # Add to the PostgreSQL database
        PostgreSQL().new_repository(
            repo_uuid4=UUID4,
            owner=owner,
            name=repo_name,
            description=description,
            visibility=visibility,
        )

        return UUID4

    @staticmethod
    def delete_repository(owner, repo_name):
        repo_path = f'data/vcs/{owner}/repositories/{repo_name}'
        if not os.path.exists(repo_path):
            raise error.RepositoryNotFound(f"Repository {repo_name} not found for {owner}")
        shutil.rmtree(repo_path)
        return True

    def add_file(self, file_path):
        try:
            self.repo.index.add([file_path])
            return True
        except Exception as e:
            raise error.GitCommandError(f"Failed to add file: {e}")

    def commit(self, message):
        try:
            self.repo.index.commit(message)
            return True
        except Exception as e:
            raise error.GitCommandError(f"Failed to commit: {e}")

    def push(self, remote_name='origin', branch_name='main'):
        try:
            remote = self.repo.remote(name=remote_name)
            remote.push(refspec=branch_name)
            return True
        except git.exc.GitCommandError as e:
            raise error.GitCommandError(f"Failed to push: {e}")

    def pull(self, remote_name='origin', branch_name='main'):
        try:
            remote = self.repo.remote(name=remote_name)
            remote.pull(refspec=branch_name)
            return True
        except git.exc.GitCommandError as e:
            raise error.GitCommandError(f"Failed to pull: {e}")

    def create_branch(self, branch_name):
        try:
            self.repo.git.branch(branch_name)
            return True
        except git.exc.GitCommandError as e:
            raise error.GitCommandError(f"Failed to create branch: {e}")

    def checkout_branch(self, branch_name):
        try:
            self.repo.git.checkout(branch_name)
            return True
        except git.exc.GitCommandError as e:
            raise error.GitCommandError(f"Failed to checkout branch: {e}")

    def walk_repo(self):
        """
        Walks through the repository directory and lists all files and folders.
        :return: A dictionary with structure {'directories': [...], 'files': [...]}
        """
        repo_structure = {'directories': [], 'files': []}
        for root, dirs, files in os.walk(self.repo_path):
            # Store directories relative to the repo root
            repo_structure['directories'].extend(os.path.relpath(os.path.join(root, d), self.repo_path) for d in dirs)
            repo_structure['files'].extend(os.path.relpath(os.path.join(root, f), self.repo_path) for f in files)
        return repo_structure

    def get_version(self):
        data = rd_config().read(self.owner, self.repo_name)
        return {
            'major': data['v_major'],
            'minor': data['v_minor'],
            'patch': data['v_patch'],
        }

    @staticmethod
    def cli():
        def greet():
            print(f"Welcome to the Raindrop Version Control System CLI.")
            print("Type 'help' for a list of commands.")
            return True

        VCS_cli = cli_handler(
            cli_name="VCS",
            greet_func=greet,
            is_main_cli=False,
            use_plugins=False
        )

        VCS_cli.register_command(
            cmd='create',
            description="Create a new repository.",
            func=VCS.cli_funcs.create_repo,
        )

        VCS_cli.register_command(
            cmd='delete',
            description="Delete a repository.",
            func=VCS.cli_funcs.delete_repo,
        )

        VCS_cli.main()
        return True

    class cli_funcs:
        @staticmethod
        def create_repo():
            try:
                owner = versioning_cli.ask_question(
                    question="Enter the owner of the repository.",
                    default="Raindrop",
                    show_default=True,
                    exit_phrase="exit",
                )
                if owner is None:
                    return True
                else:
                    if not users.exists(owner):
                        print("User not found.")
                        return True

                repo_name = versioning_cli.ask_question(
                    question="Enter the name of the repository.",
                    default="exit",
                    show_default=False,
                    exit_phrase="exit",
                )
                if repo_name is None:
                    return True
                else:
                    if VCS.repository_exists(owner, repo_name):
                        print("Repository already exists.")
                        return True

                description = versioning_cli.ask_question(
                    question="Enter a description for the repository.",
                    default="",
                    show_default=False,
                )

                visibility = versioning_cli.ask_question(
                    question="Enter the visibility of the repository.",
                    options=['private', 'public', 'unlisted'],
                )
                if visibility is None:
                    return True
            except cli_handler.exited_questioning:
                print("Cancelled.")
                return True

            success = VCS.create_repository(owner, repo_name, description, visibility)
            if success:
                print("Repository created.")
            else:
                print("Failed to create repository.")
            return True

        @staticmethod
        def delete_repo():
            try:
                owner = versioning_cli.ask_question(
                    question="Enter the owner of the repository.",
                    default="exit",
                    show_default=False,
                    exit_phrase="exit",
                )
                if owner is None:
                    return True
                else:
                    if not users.exists(owner):
                        print("User not found.")
                        return True

                repo_name = versioning_cli.ask_question(
                    question="Enter the name of the repository.",
                    default="exit",
                    show_default=False,
                    exit_phrase="exit",
                )
                if repo_name is None:
                    return True
                else:
                    if not VCS.repository_exists(owner, repo_name):
                        print("Repository not found.")
                        return True
            except cli_handler.exited_questioning:
                print("Cancelled.")
                return True

            VCS.delete_repository(owner, repo_name)
            print("Repository deleted.")
            return True