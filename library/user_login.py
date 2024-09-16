from library.storage import var, PostgreSQL, dt
from library.errors import error
import secrets
import os

class users:
    @staticmethod
    def register(username, password):
        """
        Registers a user
        :return:
        """
        assert type(username) == str, "Username must be a string."
        assert type(password) == str, "Password must be a string."
        if PostgreSQL().check_exists(username, not_exist_ok=True) is True:
            raise error.user_already_exists
        if not len(password) >= 4: raise error.password_too_short
        success = PostgreSQL().add_user(username, password)
        # Always make the first user to be created an admin. Check what their serial user ID is.
        conn = PostgreSQL().get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT * FROM accounts
            WHERE user_id = 1
            """
        )

        if cur.fetchone() is None:
            PostgreSQL().make_user_administrator(username)

        cur.close()
        conn.close()

        return success

    @staticmethod
    def delete(username):
        """
        Deletes a user
        :return:
        """
        PostgreSQL().delete_user(username)

    @staticmethod
    def exists(username):
        """
        Checks if a user exists
        :return:
        """
        return PostgreSQL().check_exists(username)

    @staticmethod
    def get_pfp(username, dir_only=False) -> bytes | str:
        """
        Returns the profile picture of the user
        :param username:
        :param dir_only:  If True, returns the directory of the pfp
        :return:
        """
        pfp_dir = f'data/users/{username}/pfp.png'
        if dir_only:
            if os.path.exists(pfp_dir):
                return pfp_dir
            else:
                return 'website/assets/img/default_pfp.png'

        if os.path.exists(pfp_dir):
            with open(pfp_dir, 'rb') as f:
                return f.read()
        else:
            with open('website/assets/img/default_pfp.png', 'rb') as f:
                return f.read()

    @staticmethod
    def get_pfp_address(username):
        return f"http://{var.get('hostname')}:2048/view/{username}/pfp"

    @staticmethod
    def get_banner(username, dir_only=False):
        """
        Returns the banner of the user
        :return:
        """
        banner_dir = f'data/users/{username}/banner.png'
        if dir_only:
            if os.path.exists(banner_dir):
                return banner_dir
            else:
                return 'website/assets/img/default_banner.jpg'

        if os.path.exists(banner_dir):
            with open(banner_dir, 'rb') as f:
                return f.read()
        else:
            with open('website/assets/img/default_banner.jpg', 'rb') as f:
                return f.read()

    @staticmethod
    def get_banner_address(username):
        return f"http://{var.get('hostname')}:2048/view/{username}/banner"

    @staticmethod
    def get_bio(username):
        """
        Returns the bio of the user
        :return:
        """
        return PostgreSQL().get_bio(username)

class user_login:
    def __init__(self, username:str=None, password=None, token=None):
        """
        A class to login to a user
        :param username:
        :param password:
        """
        if not username is None:
            self.username = username

            exists = PostgreSQL().check_exists(username)
            if not exists:
                raise error.user_nonexistant

        self.password = password

        if password is not None and token is None:
            if not PostgreSQL().get_password(username) == password:
                raise error.bad_password
        elif password is None and token is not None:
            if not PostgreSQL().validate_token(token):
                raise error.bad_token
            # Determines who the token belongs to
            self.username = PostgreSQL().get_token_owner(token)
        else:
            raise PermissionError("Either password or token must be provided.")

        self.is_admin = PostgreSQL().is_user_administrator(self.username)
        self.user_config = f'data/users/{self.username}/config.json'

    def generate_token(self):
        """
        Generates a token for the user
        :return:
        """
        token = secrets.token_urlsafe(128)
        PostgreSQL().save_token(
            belongs_to=self.username,
            token=token
        )
        return token

    def is_restricted(self):
        return PostgreSQL().is_restricted(self.username)

    def set_restricted(self, status:bool):
        return PostgreSQL().set_restricted(self.username, status)

    def list_private_repos(self):
        return PostgreSQL().list_private_repos(self.username)

    def list_public_repos(self):
        return PostgreSQL().list_public_repos(self.username)

    def create_repository(self, repo_name, description, is_private):
        """
        Register a repository in the database.
        """
        PostgreSQL().add_repository(
            owner=self.username,
            name=repo_name,
            description=description,
            is_private=is_private
        )
        repo_path = f'data/users/{self.username}/repositories/{repo_name}'
        os.makedirs(repo_path, exist_ok=True)

        # Create the .rdvcs file
        config = dt.REPO_CONFIG
        config["repo_id"] = repo_name
        config["version"] = [1,0,0]  # Major, Minor, Patch
        config["repo_name"] = repo_name
        config["description"] = description

        var.fill_json(
            file=os.path.join(repo_path, '.rdvcs'),
            data=config
        )

    def delete_repository(self, repo_name):
        """
        Deletes a repository
        """
        PostgreSQL().delete_repository(self.username, repo_name)
        repo_path = f'data/users/{self.username}/repositories/{repo_name}'
        os.system(f'rm -rf {repo_path}')

    def walk_repository(self, repo_name):
        """
        Walks through the repository
        """
        return PostgreSQL().walk_repository(repo_name, self.username)