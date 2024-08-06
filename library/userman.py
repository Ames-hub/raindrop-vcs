from library.versioncontrolsystem import versionControlSystem
from library.storage import var, dt, PostgreSQL
import secrets
import os

class userman:
    def __init__(self, username:str=None, password:str=None, token=None):
        """
        A class to manage users.
        :param username:
        :param password:
        """
        self.user_config = f'data/users/{username}/config.json'
        self.registered = self.exists()
        if username is not None:
            if self.verify_password(password) is True:
                self.token = self.generate_token()
            else:
                raise PermissionError('Invalid password.')
        else:
            assert token is not None, 'token must be provided.'
            self.token = token

        self.username = username
        self.postgre = PostgreSQL()

    def generate_token(self, save=False):
        """
        Generates a token for the user
        :return:
        """
        token = secrets.token_urlsafe(128)
        if save:
            self.postgre.save_token(belongs_to=self.username, token=token)
        return token

    def register(self, password) -> bool:
        """
        Registers a user
        :param password: The new password of the user
        :return:
        """
        user_data = dt.USER_CONFIG
        user_data['username'] = self.username
        user_data['password'] = password

        var.fill_json(
            file=self.user_config,
            data=user_data
        )
        return True

    def exists(self) -> bool:
        """
        Checks if the user exists
        :return:
        """
        return os.path.exists(f'data/users/{self.username}/config.json')

    def list_repositories(self) -> dict:
        """
        Lists all repositories of the account.
        """
        # name: desc
        repositories = {}
        repo_dir = os.path.join('data', 'users', str(self.username), 'repositories')
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir, exist_ok=True)

        if len(os.listdir(repo_dir)) > 0:
            for repo in os.listdir(repo_dir):
                repositories[repo] = var.get(
                    f'data/users/{self.username}/repositories/{repo}/config.json',
                    'description',
                    dt_default=dt.REPO_CONFIG
                )
        else:
            repositories = {'error': 'No repositories found.'}

        return repositories

    def verify_password(self, password) -> bool:
        """
        Verifies the password of the user
        :return:
        """
        user_password = var.get(self.user_config, 'password', dt_default=dt.USER_CONFIG)
        if user_password == password:
            return True
        else:
            return False

    def get_pfp(self, dir_only=False) -> bytes | str:
        """
        Returns the profile picture of the user
        :param dir_only:  If True, returns the directory of the pfp
        :return:
        """
        pfp_dir = f'data/users/{self.username}/pfp.png'
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

    def get_pfp_address(self):
        return f"http://{var.get('hostname')}:2048/view/{self.username}/pfp"

    def get_banner(self, dir_only=False):
        """
        Returns the banner of the user
        :return:
        """
        banner_dir = f'data/users/{self.username}/banner.png'
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

    def get_banner_address(self):
        return f"http://{var.get('hostname')}:2048/view/{self.username}/banner"

    def get_bio(self):
        """
        Returns the bio of the user
        :return:
        """
        user_bio = var.get(file=self.user_config, key='bio', dt_default=dt.USER_CONFIG)
        if user_bio is not None and user_bio != '':
            return user_bio
        else:
            return "Feeling new? Add a bio!"

    def interact_with_repo(self, repo_id):
        versionControlSystem(
            token=self.token,
            repo_id=repo_id
        )
