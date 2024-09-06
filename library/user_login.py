from library.storage import var, PostgreSQL
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
        PostgreSQL().add_user(username, password)

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
        return PostgreSQL().user_exists(username)

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

class userman:
    def __init__(self, username:str=None, password=None, token=None):
        """
        A class to manage users. Enter None type as password to enter restricted viewing mode.
        :param username:
        :param password:
        """
        self.username = username

        exists = PostgreSQL().user_exists(username)
        if not exists:
            raise error.user_nonexistant

        self.password = password
        self.token = token
        self.user_config = f'data/users/{username}/config.json'

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

    def is_restricted(self):
        return PostgreSQL().is_restricted(self.username)

    def set_restricted(self, status:bool):
        return PostgreSQL().set_restricted(self.username, status)
