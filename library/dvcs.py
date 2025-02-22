from library.cmd_interface import cli_handler
from library.errors import error
import datetime
import sqlite3
import shutil
import uuid
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

class rd_config:
    """
    Raindrop Configuration System for a repository.
    Manages the entire .rdc directory within a repository and its contents.
    """
    def __init__(self, repo_owner:str, repo_name:str):
        self.rdc_file = None
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def commit_line(self, semver, line_content, line_number, author, commit_date=None):
        """
        Write a commit to the database file.

        :param semver: The semantic version of the commit
        :param line_content: The content of the line changed
        :param line_number: The line number of the line changed
        :param author: The author of the commit
        :param commit_date: The date of the commit
        :return:
        """
        db_file = f'data/vcs/{self.repo_owner}/repositories/{self.repo_name}/.rdc/vcs.sqlite3'
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        commit_date = str(commit_date) if commit_date is not None else str(datetime.datetime.now())

        cur.execute(
            f"INSERT INTO commits VALUES (?, ?, ?, ?, ?)",
            (semver, line_content, line_number, author, commit_date)
        )

        conn.commit()

    def exists(self) -> bool:
        self.rdc_file = f'data/vcs/{self.repo_owner}/repositories/{self.repo_name}/.rdc/cfg'
        return os.path.exists(self.rdc_file)

    def read_cfg(self) -> dict:
        """
        Read the RDC file for a repository.

        :return:
        """
        self.rdc_file = f'data/vcs/{self.repo_owner}/repositories/{self.repo_name}/.rdc/cfg'
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

    def read_db(self, table_name:str) -> list:
        """
        Read the database file for a repository.

        :param table_name: The name of the table to read from.
        :return:
        """
        db_file = f'data/vcs/{self.repo_owner}/repositories/{self.repo_name}/.rdc/vcs.sqlite3'
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name}")
        data = cur.fetchall()

        # Arrange the data into a list of dictionaries
        data = [dict(zip([desc[0] for desc in cur.description], row)) for row in data]

        return data

    def register(self, description, visibility) -> uuid.UUID:
        """
        Register a new RDC file for a repository by writing its configuration to a file.
        This function will also add the UUID to the PostgreSQL database.
        This is not to be used for updating an existing RDC file.

        :param description:
        :param visibility:
        :return:
        """
        if not visibility in ['private', 'public', 'unlisted']:
            raise error.InvalidRepoVisibility(f"Invalid visibility {visibility}")

        if self.rdc_file is None:
            self.rdc_file = f'data/vcs/{self.repo_owner}/repositories/{self.repo_name}/.rdc/cfg'
            os.makedirs(os.path.dirname(self.rdc_file), exist_ok=True)

        if os.path.exists(self.rdc_file):
            raise error.RDC_AlreadyExists(f"RDC already exists for {self.repo_name}")

        # Parse the description to allow for any/all problematic characters.
        description = description.replace("\n", "<br>")

        UUID = uuid.uuid4()

        try:
            with open(self.rdc_file, 'w') as f:
                f.write(f"owner={self.repo_owner}\n")
                f.write(f"name={self.repo_name}\n")
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

        # Create the sqlite3 db file
        db_file = f"data/vcs/{self.repo_owner}/repositories/{self.repo_name}/.rdc/vcs.sqlite3"

        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        table_dict = {
            "commits": {
                "Semver": "TEXT NOT NULL PRIMARY KEY",
                "line_content": "TEXT NOT NULL",
                "line_number": "INTEGER NOT NULL",
                "author": "TEXT NOT NULL",
                "commit_date": "TEXT NOT NULL",
            },
        }

        for table_name, table_columns in table_dict.items():
            cur.execute(f"CREATE TABLE {table_name} ({', '.join([f'{k} {v}' for k, v in table_columns.items()])})")

        conn.commit()

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
            self.rdc_file = f'data/vcs/{repo_owner}/repositories/{repo_name}/.rdc/cfg'

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

class vmsystem:
    """
    Version Memory/Management System for an existing repository.
    """
    def __init__(self, owner, repo_name:str):
        self.repo_name = repo_name
        self.owner = owner
        if not rd_config(repo_owner=owner, repo_name=repo_name).exists():
            raise error.RDCNotFound(f"RDC not found for {repo_name}. Does the repository exist?")

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
        rdc = rd_config(repo_owner=self.owner, repo_name=self.repo_name)
        rdc_data = rdc.read_cfg()
        version = [int(rdc_data['v_major']), int(rdc_data['v_minor']), int(rdc_data['v_patch'])]

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
        rdc.update('v_major', version[0], self.repo_name, self.owner)
        rdc.update('v_minor', version[1], self.repo_name, self.owner)
        rdc.update('v_patch', version[2], self.repo_name, self.owner)

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

            vmsystem(owner=owner, repo_name=repo_name).increment_version(ver_type=ver_type)
            print("Version added.")
            return True

class VCS:
    def __init__(self, owner, repo_name):
        self.repo_path = f'data/vcs/{owner}/repositories/{repo_name}'
        self.owner = owner
        self.repo_name = repo_name

        if not self.repository_exists(owner, repo_name):
            raise error.RepositoryNotFound(f"Repository {repo_name} not found for {owner}")

    @staticmethod
    def list_public_repositories(owner=None):
        if owner is None:
            base_dir = 'data/vcs/'
            all_repos = {}
            if not os.path.exists(base_dir):
                return all_repos
            for user in os.listdir(base_dir):
                user_dir = os.path.join(base_dir, user, 'repositories')
                if os.path.exists(user_dir):
                    for repo in os.listdir(user_dir):
                        if os.path.isdir(os.path.join(user_dir, repo)):
                            rdc_data = rd_config(user, repo).read_cfg()
                            if rdc_data['visibility'] == 'public':
                                all_repos[repo] = rdc_data.get('description', 'No description')
            return all_repos
        else:
            repos_dir = f'data/vcs/{owner}/repositories/'
            if not os.path.exists(repos_dir):
                return {}

            all_repos = {}
            for repo in os.listdir(repos_dir):
                if os.path.isdir(os.path.join(repos_dir, repo)):
                    rdc_data = rd_config(owner, repo).read_cfg()
                    if rdc_data['visibility'] == 'public':
                        all_repos[repo] = rdc_data.get('description', 'No description')

            return all_repos  # example output: {'repo1': 'Description', 'repo2': 'Description'}

    @staticmethod
    def repository_exists(owner, repo_name):
        return os.path.exists(f'data/vcs/{owner}/repositories/{repo_name}/.rdc/cfg')

    @staticmethod
    def create_repository(owner, repo_name, description='', visibility='private') -> uuid.UUID:
        repo_path = f'data/vcs/{owner}/repositories/{repo_name}'
        if os.path.exists(repo_path):
            raise error.RepositoryAlreadyExists(f"Repository {repo_name} already exists for {owner}")
        os.makedirs(repo_path, exist_ok=True)

        UUID4 = rd_config(owner, repo_name).register(
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
        data = rd_config(self.owner, self.repo_name).read_cfg()
        return {
            'major': data['v_major'],
            'minor': data['v_minor'],
            'patch': data['v_patch'],
        }

    def commit(self, author, new_file_data:dict, commit_date=None, vertype=None):
        """
        Commit the changes for a singular file to the repository.

        :param author: The author of the commit
        :param new_file_data: The data of the file to commit in the format {line_number: line_content}
        :param commit_date:  The date of the commit (default is now)
        :param vertype: The type of version change (MAJOR, MINOR, PATCH) default is determined by the number of lines changed
        :return:
        """

        if not type(new_file_data) is dict:
            raise ValueError(f"Invalid file type: {type(new_file_data)}")
        if not all(type(k) is int and type(v) is str for k, v in new_file_data.items()):
            raise ValueError(f"Invalid file data: {new_file_data}")
        if not commit_date is None and not type(commit_date) is datetime.datetime and not type(commit_date) is str:
            raise ValueError(f"Invalid commit date: {commit_date}, {type(commit_date)}")

        if not os.path.exists(f'data/vcs/{self.owner}'):
            raise error.UserNotFound(f"User {self.owner} not found.")

        lines_changed = len(new_file_data)
        vms = vmsystem(owner=self.owner, repo_name=self.repo_name)
        if vertype is None:
            vms.increment_version(amount_lines_changed=lines_changed)
        else:
            vms.increment_version(ver_type=vertype)

        rdc = rd_config(self.owner, self.repo_name)

        semver = rdc.read_cfg()['v_major'] + '.' + rdc.read_cfg()['v_minor'] + '.' + rdc.read_cfg()['v_patch']

        for line_content, line_number in new_file_data:
            if commit_date is None:
                commit_date = datetime.datetime.now()

            rdc.commit_line(
                author=author,
                line_content=line_content,
                line_number=line_number,
                commit_date=commit_date,
                semver=semver
            )

        return True

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
            from library.user_login import users
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
            from library.user_login import users
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