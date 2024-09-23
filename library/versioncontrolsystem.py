from library.storage import PostgreSQL
from library.errors import error

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
            """
            SELECT EXISTS(SELECT 1 FROM repositories WHERE owner = %s AND name = %s AND is_private = FALSE)
            """,
            (owner, repo_name)
        )
        exists = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return exists

# noinspection PyMethodMayBeStatic
class repository_handler:
    def __init__(self, username, repo_name):
        """
        Intended for pre-existing repositories only.
        Intended for authorized access only.

        :param username:
        :param repo_name:
        """
        self.owner = username
        self.repo_name = repo_name

        if not self.check_repo_exists(not_exist_ok=True):
            raise error.repository_not_found(repo_name)

        # If the owner of the repository is not what's set as 'username', raise a permission error.
        if not PostgreSQL().get_repository_owner(self.repo_name) == self.owner:
            raise error.insufficient_permissions

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

    def set_privacy(self, is_private):
        return PostgreSQL().update_repository_is_private(self.owner, self.repo_name, is_private)

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
        repo_exists = vcs.repository_exists(self.owner, self.repo_name)
        # If the repository does not exist, raise an error if not_exist_ok is False
        if not_exist_ok:
            return repo_exists
        if not repo_exists:
            raise error.repository_not_found

    def walk_repo(self):
        """
        Walks the repository and returns a list of files and directories.
        :return:
        """
        return PostgreSQL().walk_repository(self.owner, self.repo_name)
