#!/usr/bin/env python3.12
"""
This is the file that users will interact with repositories (via the cli) with.
There will be a gui method in the future, but for now, this is all.

It is interacted with by calling the file and then adding arguments to the command line.
for a raw py file, this would look like:
python3.12 rd_client.py init

For a compiled binary (or an exe file), this would look like:
rdc init
"""

import platform
import datetime
import sqlite3
import fnmatch
import shutil
import uuid
import sys
import os

args = [arg.lower() for arg in sys.argv]

def determine_install_dir():
    system = platform.system()
    if system in ["Linux", "Darwin"]:
        return "/usr/local/bin/"
    elif system == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "bin")
    else:
        return None

def setup_command():
    script_path = os.path.abspath(__file__)
    command_name = "rdc"
    file_name = os.path.basename(script_path).split(".")[0] # Remove the extension

    system = platform.system()

    if system == "Windows":
        exe_dir = os.path.join(os.path.dirname(script_path), file_name, ".exe")
        if os.path.exists(exe_dir):
            # If the Exe file exists, use that instead
            script_path = exe_dir

    if not os.path.isfile(script_path):
        print(f"Error: The script '{script_path}' does not exist.")
        return


    if system in ["Linux", "Darwin"]:  # macOS is 'Darwin'
        install_dir = determine_install_dir()
        target_path = os.path.join(install_dir, command_name)

        # Copy script to global bin
        shutil.copy(script_path, target_path)
        os.chmod(target_path, 0o755)  # Make it executable
        print(f"✅ Command '{command_name}' is now globally available.")
    elif system == "Windows":
        install_dir = determine_install_dir()
        os.makedirs(install_dir, exist_ok=True)
        target_path = os.path.join(install_dir, command_name + ".bat")

        # Create a batch file to run the Python script
        with open(target_path, "w") as bat_file:
            bat_file.write(f"@echo off\npython3.12 {script_path} %*\n")

            # Add to PATH if needed
            path_env = os.environ.get("PATH", "")
            if install_dir not in path_env:
                os.system(f'setx PATH "%PATH%;{install_dir}"')
                print(f"🔄 Added '{install_dir}' to PATH. Restart terminal to use '{command_name}'.")

            print(f"✅ Command '{command_name}' is now available globally.")
    else:
        print("❌ Unsupported OS.")
        return

    # Create a file to indicate that the command is installed
    with open(os.path.join(install_dir, "rdc_installed"), "w") as f:
        f.write("This file indicates that the Raindrop Client command is installed. Please do not delete.")

    return install_dir

def read_author_file():
    file_path = r"C:\ProgramData\Raindrop\author.txt" if os.name == 'nt' else "/etc/raindrop/author.txt"
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    except PermissionError:
        print("Permission error creating author file's directory. Please run this file with elevated permissions.\n"
              "Couldn't access:", file_path)
        sys.exit(1)
    if not os.path.exists(file_path):
        while True:
            print("Author file not found. Please enter your Raindrop author name. (case sensitive, no spaces)")
            author = input(">>> ")
            if " " in author:
                print("Author name cannot contain spaces.")
                continue
            if len(author) <= 0:
                print("Author name cannot be empty.")
                continue

            try:
                with open(file_path, 'w') as file:
                    file.write(author)
            except PermissionError:
                print("Permission error writing author file. Please run this file with elevated permissions.\n"
                      "Couldn't access:", file_path)
                sys.exit(1)

            break
    else:
        try:
            with open(file_path, 'r') as file:
                author = file.read().strip()
        except PermissionError:
            print("Permission error reading author file. Please run this file with elevated permissions.\n"
                  "Couldn't access:", file_path)
            sys.exit(1)

    return author

def get_author(func):
    def wrapper(*args, **kwargs):
        author = read_author_file()

        return func(*args, **kwargs, author=author)
    return wrapper

class error:
    class RDC_AlreadyExists(Exception):
        def __init__(self, message):
            self.code_number = 17
            super().__init__(message)

    class RDCNotFound(Exception):
        def __init__(self, message):
            self.code_number = 18
            super().__init__(message)

    class RDCWriteError(Exception):
        def __init__(self, message):
            self.code_number = 19
            super().__init__(message)

    class InvalidRDCData(Exception):
        def __init__(self, message):
            self.code_number = 20
            super().__init__(message)

    class InvalidRDCRepoVisibility(Exception):
        def __init__(self, message):
            self.code_number = 21
            super().__init__(message)

class rd_config:
    """
    Raindrop Configuration System for a repository.
    Manages the entire .rdc directory within a repository and its contents.
    """
    def __init__(self):
        self.rdc_file = None

    @staticmethod
    def commit_line(semver, line_content, line_number, author, commit_date=None):
        """
        Write a commit to the database file.

        :param semver: The semantic version of the commit
        :param line_content: The content of the line changed
        :param line_number: The line number of the line changed
        :param author: The author of the commit
        :param commit_date: The date of the commit
        :return:
        """
        db_file = '.rdc/vcs.sqlite3'
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        commit_date = str(commit_date) if commit_date is not None else str(datetime.datetime.now())

        cur.execute(
            f"INSERT INTO commits VALUES (?, ?, ?, ?, ?)",
            (semver, line_content, line_number, author, commit_date)
        )

        conn.commit()

    @staticmethod
    def exists() -> bool:
        return os.path.exists('.rdc/metadata.txt')

    @staticmethod
    def read_cfg() -> dict:
        """
        Read the RDC file for a repository.

        :return:
        """
        rdc_file = os.path.join(os.getcwd(), '.rdc/metadata.txt')
        if not os.path.exists(rdc_file):
            print("Repository not initialized. Please run init command to initialize the repository.")
            sys.exit(1)
        with open(rdc_file, 'r') as f:
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

    @staticmethod
    def read_db(table_name:str) -> list:
        """
        Read the database file for a repository.

        :param table_name: The name of the table to read from.
        :return:
        """
        db_file = '.rdc/vcs.sqlite3'
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name}")
        data = cur.fetchall()

        # Arrange the data into a list of dictionaries
        data = [dict(zip([desc[0] for desc in cur.description], row)) for row in data]

        return data

    @staticmethod
    @get_author
    def register(description, visibility, repo_name, author) -> uuid.UUID:
        """
        Register a new RDC file for a repository by writing its configuration to a file.
        This function will also add the UUID to the PostgreSQL database.
        This is not to be used for updating an existing RDC file.

        :param description: The description of the repository
        :param visibility: The visibility of the repository (private, public, unlisted)
        :param repo_name: The name of the repository
        :param author: The owner of the repository
        :return:
        """
        if not visibility in ['private', 'public', 'unlisted']:
            print("Invalid visibility. Please use 'private', 'public', or 'unlisted'.")
            sys.exit(1)

        rdc_file = '.rdc/metadata.txt'
        os.makedirs('.rdc', exist_ok=True)

        if os.path.exists(rdc_file):
            print("Repository already initialized.")
            sys.exit(1)

        # Parse the description to allow for any/all problematic characters.
        description = description.replace("\n", "<br>")

        UUID = uuid.uuid4()

        try:
            with open(rdc_file, 'w') as f:
                f.write(f"owner={author}\n")
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

        # Create the sqlite3 db file
        db_file = f".rdc/vcs.sqlite3"

        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        table_dict = {
            "commits": {
                "Semver": "TEXT NOT NULL",
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

    def update(self, key, value, repo_name):
        """
        Update a key in the RDC file.

        :param key: The key to update
        :param value: The value to update the key to
        :param repo_name: The name of the repository
        :return:
        """
        if self.rdc_file is None:
            self.rdc_file = '.rdc/metadata.txt'

        if not os.path.exists(self.rdc_file):
            print(f"Repository {repo_name} not initialized. Please run init command to initialize the repository.")
            sys.exit(1)

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

def ask(question:str, filter_func):
    while True:
        print(question)
        response = input(">>> ")
        if filter_func(response) is True:
            return response
        else:
            print("Invalid response. Please try again.")

def get_rd_ignore():
    ignore_file = '.rdignore'
    if not os.path.exists(ignore_file):
        return []

    with open(ignore_file, 'r') as f:
        ignore_list = f.read().split('\n')

    ign_dict = {
        "directories": [],
        "mimetypes": [],
        "files": [],
    }

    for ignore in ignore_list:
        ignore = ignore.strip()
        if not ignore or ignore.startswith('#'):
            continue
        if ignore.startswith("type:"):
            ign_dict['mimetypes'].append(ignore.replace("type:", "").strip())
        elif os.path.isdir(ignore):
            ign_dict['directories'].append(os.path.abspath(ignore))
        else:
            ign_dict['files'].append(ignore)

    return ign_dict

def is_ignored(file_path, ignore_dict):
    for pattern in ignore_dict['files']:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    for directory in ignore_dict['directories']:
        if file_path.startswith(directory):
            return True
    for mimetype in ignore_dict['mimetypes']:
        if file_path.endswith(mimetype):
            return True
    return False

rdc = rd_config()

def parse_kwargs():
    kwargs = {}
    for arg in sys.argv[1:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            kwargs[key] = value
    return kwargs

if __name__ == "__main__":
    kwargs = parse_kwargs()
    print("Raindrop Client v1.0.0")
    print(f"{len(sys.argv)} arguments passed. {len(kwargs)} kwargs passed.")
    print("Type 'rdc help' for a list of commands and general help.")

    if not os.path.exists(os.path.join(determine_install_dir(), "rdc_installed")):
        print("We detected that the RDC shortcut is not installed.")
        print("We're going to install it now.\n")
        if platform.system() == "Linux":
            print("Please note! You may have to start this script with sudo or elevated permissions for it to work.")

        try:
            setup_command()
        except PermissionError:
            print("Permission error creating command. Please run this file with elevated permissions.")
            sys.exit(1)

if "init" in args:
    repo_name = ask("Enter the name of the repository:", lambda x: len(x) > 0)
    repo_desc = ask("Describe your repository:", lambda x: len(x) > 0)
    visibility = ask(
        "Enter the visibility of the repository on raindrop instances (private, public, unlisted):",
        lambda x: x in ['private', 'public', 'unlisted']
    )

    try:
        UUID = rdc.register(
            description=repo_desc,
            visibility=visibility,
            repo_name=repo_name
        )
    except error.RDC_AlreadyExists as e:
        print(e)
        sys.exit(1)

    print(f"Repository {repo_name} registered with UUID {UUID}")
elif "help" in args:
    print("""
Raindrop Client (rdc) - Command Line Interface

Usage:
  rdc <command> [options]

Commands:
  - init                Initialize a new repository.
  
  - commit <file>       Commit changes to a file. Use '-a' to commit all files.
    Options:
      --line_range=start-end  Specify a range of lines to commit (e.g., --line_range=10-20).
  
  - help                Show this help message.

Examples:
  rdc init
  rdc commit myfile.txt
  rdc commit -a
  rdc commit myfile.txt --line_range=10-20
""")
elif "commit" in args:
    commit_list = []
    try:
        file_to_commit = args[2]
        if file_to_commit == "-a":
            # Commit all files in the directory and subdirectories
            for root, dirs, files in os.walk(os.getcwd()):
                for file in files:
                    commit_list.append(os.path.join(root, file))
        else:
            file_to_commit = os.path.join(os.getcwd(), file_to_commit)
            commit_list.append(file_to_commit)
    except IndexError:
        print("Please specify a file to commit by adding it as an argument.")
        sys.exit(1)

    commit_message = ask("Enter a commit message:", lambda x: len(x) > 0)
    rd_ignore = get_rd_ignore()

    if len(commit_list) <= 0:
        print("No files to commit.")
        sys.exit(1)

    for file_to_commit in commit_list:
        if not os.path.exists(file_to_commit):
            print(f"File does not exist at \"{file_to_commit}\"")
            sys.exit(1)

        file_is_ignored = is_ignored(file_to_commit, rd_ignore)
        if file_is_ignored:
            print(f"File {file_to_commit} is ignored.")
            continue

        # Reads the file and separates it into lines
        try:
            with open(file_to_commit, 'r') as f:
                lines = f.read().split('\n')
        except UnicodeDecodeError:
            print(f"File {file_to_commit} is not a text file.")
            continue
        except PermissionError:
            print(f"Permission error reading file {file_to_commit}. Please run rdc with elevated permissions.")
            continue
        except FileNotFoundError:
            print(f"File {file_to_commit} not found?")
            continue

        # Kwarg option.
        line_range = parse_kwargs().get('line_range', None)
        if line_range is not None:
            try:
                r_start, r_end = line_range.split('-')
                r_start = int(r_start)
                r_end = int(r_end)
            except ValueError:
                print("Invalid line range. Please use the format 'start-end'")
                sys.exit(1)

            if r_start > r_end or r_start < 0 or r_end > len(lines) or r_start == r_end or r_start > len(lines):
                print("Line range out of bounds.")
                sys.exit(1)

            lines = lines[r_start:r_end]
            print(f"Committing lines {r_start} to {r_end} in file {file_to_commit}")
        else:
            print(f"Committing all lines in file {file_to_commit}")

        author = read_author_file()

        rdc_data = rdc.read_cfg()
        v_major = int(rdc_data['v_major'])
        v_minor = int(rdc_data['v_minor'])
        v_patch = int(rdc_data['v_patch'])

        # Increment the patch version based on number of lines changed
        lines_changed = len(lines)
        if lines_changed > 700:
            v_major += 1
        elif 100 <= lines_changed <= 700:
            v_minor += 1
        else:
            v_patch += 1

        semver = f"{v_major}.{v_minor}.{v_patch}"

        for i, line in enumerate(lines):
            rdc.commit_line(
                semver=semver,
                line_content=line,
                line_number=i,
                author=author
            )