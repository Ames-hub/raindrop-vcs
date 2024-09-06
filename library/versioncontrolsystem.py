from library.storage import PostgreSQL
from library.errors import error
from datetime import datetime
import hashlib
import os

class vcs:
    """
    A class Meant especially for unauthorized access (public repositories and such)
    """
    @staticmethod
    def list_pub_repositories(owner):
        return PostgreSQL().list_public_repos(owner)

    @staticmethod
    def repository_exists(owner, repo_name):
        conn = PostgreSQL().get_connection()
        cursor = conn.cursor()

        # Do not show if a private repository exists.
        cursor.execute(
            'SELECT EXISTS(SELECT 1 FROM repositories WHERE owner = %s AND name = %s AND is_private = FALSE)',
            (owner, repo_name)
        )
        exists = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return exists

# noinspection PyMethodMayBeStatic
class repository_handler:
    def __init__(self, owner, repo_name):
        """
        Intended for pre-existing repositories only.
        :param owner:
        :param repo_name:
        """
        self.owner = owner
        self.repo_name = repo_name
        self.repo_path = f'data/users/{self.owner}/repositories/{self.repo_name}'

        if not self.check_repo_exists(not_exist_ok=True):
            raise error.repository_not_found(repo_name)

    def get_is_private(self):
        conn = PostgreSQL().get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT is_private FROM repositories WHERE name = %s AND owner = %s',
            (self.repo_name, self.owner)
        )
        is_private = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return is_private

    def get_description(self):
        conn = PostgreSQL().get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT description FROM repositories WHERE name = %s AND owner = %s',
            (self.repo_name, self.owner)
        )
        description = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return description

    def check_repo_exists(self, not_exist_ok=False):
        repo_exists = os.path.exists(self.repo_path)
        # If the repository does not exist, raise an error if not_exist_ok is False
        if not_exist_ok:
            return repo_exists
        if not repo_exists:
            raise error.repository_not_found

    def push_file(self, file_rel_dir, file_bytes, commit_message):
        self.check_repo_exists()

        file_version_id = self.get_new_version_id(file_rel_dir)

        # Store the file's new version
        dest_path = os.path.join(self.repo_path, file_rel_dir, file_version_id)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Write bytes to the file
        with open(dest_path, 'wb') as f:
            f.write(file_bytes)

        # Create a commit entry in the database
        self.create_commit(file_rel_dir, file_version_id, commit_message)

    def get_new_version_id(self, file_rel_dir):
        file_path = os.path.join(self.repo_path, file_rel_dir)
        file_exists = os.path.exists(file_path)

        version_id = "v1"
        if file_exists:
            current_versions = os.listdir(file_path)
            last_version = max(current_versions)
            version_number = int(last_version[1:]) + 1
            version_id = f"v{version_number}"

        return version_id

    def create_commit(self, file_rel_dir, file_version_id, commit_message):
        conn = PostgreSQL().get_connection()
        cursor = conn.cursor()

        commit_id = self.generate_commit_id()
        timestamp = datetime.now()

        # Fetch repo_id for the current repository
        cursor.execute('SELECT repo_id FROM repositories WHERE name = %s AND owner = %s', (self.repo_name, self.owner))
        repo_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO commits (commit_id, repo_id, owner, file_name, file_version_id, message, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            commit_id, repo_id, self.owner, file_rel_dir, file_version_id,
            commit_message, timestamp
        ))

        conn.commit()
        cursor.close()
        conn.close()

    def generate_commit_id(self):
        return hashlib.sha256(f"{self.repo_name}{datetime.now()}".encode()).hexdigest()

    def list_files(self):
        self.check_repo_exists()
        files_list = []
        for file_name in os.listdir(self.repo_path):
            file_path = os.path.join(self.repo_path, file_name)
            if os.path.isdir(file_path):
                versions = os.listdir(file_path)
                latest_version = max(versions)
                files_list.append((file_name, latest_version))
        return files_list

    def get_file_versions(self, file_name):
        file_path = os.path.join(self.repo_path, file_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError

        return os.listdir(file_path)

    def get_files_for_version(self, version_id):
        """
        Retrieve all files for a specific version of the repository.

        :param version_id: The version ID to retrieve files for.
        :return: A dictionary with file paths and their content in bytes.
        """
        self.check_repo_exists()

        files_content = {}
        for root, dirs, files in os.walk(self.repo_path):
            for file_name in files:
                file_version_path = os.path.join(root, file_name, version_id)
                if os.path.exists(file_version_path):
                    with open(file_version_path, 'rb') as f:
                        files_content[file_name] = f.read()
        return files_content

    def get_file_for_version(self, file_rel_dir, version_id):
        """
        Retrieve a specific file for a specific version of the repository.

        :param file_rel_dir: The relative directory of the file within the repository.
        :param version_id: The version ID to retrieve the file for.
        :return: The content of the file in bytes.
        :raises FileNotFoundError: If the file or version does not exist.
        """
        self.check_repo_exists()

        file_version_path = os.path.join(self.repo_path, file_rel_dir, version_id)
        if not os.path.exists(file_version_path):
            raise FileNotFoundError(f"File '{file_rel_dir}' with version '{version_id}' does not exist.")

        with open(file_version_path, 'rb') as f:
            return f.read()
