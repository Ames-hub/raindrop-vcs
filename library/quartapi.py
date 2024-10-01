from library.versioncontrolsystem import repository_handler, vcs
from library.user_login import user_login, users
from library.storage import var, PostgreSQL
from library.webui import webgui
from library.errors import error
import quart_cors
import functools
import datetime
import requests
import uvicorn
import logging
import quart
import sys
import re
import os

os.makedirs('data/users/', exist_ok=True)

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s'
)

# Specify the path to the templates directory
template_dir = os.path.join(os.getcwd(), 'website/templates')
DEBUG = bool(os.environ.get("DEBUG", False))
app = quart.Quart(__name__, template_folder=template_dir)
quart_cors.cors(app, allow_origin='*')

@app.errorhandler(error.user_nonexistant)
async def handle_user_nonexistant(err: error.user_nonexistant):
    return {
        'error': 'User does not exist',
        'code': err.code_number
    }, 404

@app.errorhandler(error.user_already_exists)
async def handle_user_already_exists(err: error.user_already_exists):
    return {
        'error': 'User already exists',
        'code': err.code_number
    }, 409

@app.errorhandler(error.bad_token)
async def handle_bad_token(err: error.bad_token):
    return {
        'error': 'Bad token',
        'code': err.code_number
    }, 401

@app.errorhandler(error.restricted_account)
async def handle_restricted_account(err: error.restricted_account):
    return {
        'error': 'Your account is restricted',
        'code': err.code_number
    }, 403

@app.errorhandler(error.bad_password)
async def handle_bad_password(err: error.bad_password):
    return {
        'error': 'Bad username or password',
        'code': err.code_number
    }, 401

@app.errorhandler(error.json_content_type_only)
async def wrong_content_type(err: error.json_content_type_only):
    return {
        'error': 'Content-Type must be application/json',
        'code': err.code_number
    }, 500

def docker_image_exists(image_name, tag='latest'):
    """
    Check if a Docker image exists in the Docker Hub registry.

    :param image_name: Name of the Docker image (e.g., 'library/ubuntu')
    :param tag: Tag of the Docker image (default is 'latest')
    :return: True if the image exists, False otherwise
    """
    url = f'https://registry.hub.docker.com/v2/repositories/library/{image_name}/tags/{tag}/'
    response = requests.head(url)
    return response.status_code == 200

class QuartAPI:
    @staticmethod
    def run():
        # Redirect stdout and stderr to /dev/null or NUL on Windows
        with open(os.devnull, 'w') as devnull:
            if not DEBUG:
                sys.stdout = devnull
                sys.stderr = devnull
            uvicorn.run(
                app,
                host='0.0.0.0',
                port=var.get('api.port'),
            )

    @staticmethod
    def require_json(api_function):
        """
        Decorator to ensure that the request content type is application/json
        :param api_function:
        :return:
        """
        @functools.wraps(api_function)
        async def wrapper(*args, **kwargs):
            if quart.request.content_type != 'application/json':
                raise error.json_content_type_only
            return await api_function(*args, **kwargs)
        return wrapper

    @staticmethod
    def require_authentication(api_function):
        @functools.wraps(api_function)
        async def wrapper(*args, **kwargs):
            # Get the token from the request headers and remove the "Bearer " part
            token = quart.request.headers.get('Authorization', None).split(" ")[1]

            # If token is not in headers, get it from the POST data
            if not token:
                data = await quart.request.get_json()
                token = data.get('token')

            # Validate the token
            if PostgreSQL().validate_token(token) is True:
                user = user_login(token=token)

                if user.is_restricted():
                    raise error.restricted_account

                return await api_function(*args, user=user, **kwargs)
            else:
                # Raise an error if the token is not valid
                raise error.bad_token

        return wrapper

    @staticmethod
    def administrator_only(api_function):
        @functools.wraps(api_function)
        async def wrapper(*args, **kwargs):
            # Get the token from the request headers and remove the "Bearer " part
            token = quart.request.headers.get('Authorization', None).split(" ")[1]

            # If token is not in headers, get it from the POST data
            if not token:
                data = await quart.request.get_json()
                token = data.get('token')

            # Validate the token
            if PostgreSQL().validate_token(token) is True:
                user = user_login(token=token)

                if not user.is_restricted():
                    raise error.restricted_account

                return await api_function(*args, user=user, **kwargs)
            else:
                # Raise an error if the token is not valid
                raise error.bad_token

        return wrapper

class view_routes:
    @staticmethod
    @app.route('/view/<username>/pfp', methods=['GET'])
    async def get_pfp(username):
        pfp: str = users.get_pfp(username=username, dir_only=True)
        return await quart.send_file(pfp), 200

    @staticmethod
    @app.route('/view/<username>/banner', methods=['GET'])
    async def get_banner(username):
        banner_data = users.get_banner(username, dir_only=True)
        return await quart.send_file(banner_data), 200

    @staticmethod
    @app.route('/view/<username>/bio', methods=['GET'])
    async def get_bio(username):
        return users.get_bio(username), 200

    @staticmethod
    @app.route('/view/<account>/<repository>', methods=['GET'])
    async def get_repository(account, repository):
        # Just checks if the repository exists. Most backend happens else where.
        try:
            repository_handler(account, repository)
        except error.repository_not_found:
            # Responds with a 404 error if the repository does not exist
            return await quart.send_file('website/404.html'), 404

        # Render the repository page
        return await quart.render_template(
            'repository.html',
            username=account,
            repo_name=repository,
        )

    @staticmethod
    @app.route('/view/<username>', methods=['GET'])
    async def get_account(username):
        if users.exists(username):
            return await quart.render_template(
                template_name_or_list='account.html',
                username=username,
                pfp_address=users.get_pfp_address(username),
                banner_address=users.get_banner_address(username),
                user_bio=users.get_bio(username),
            ), 200
        else:
            # Responds with a 404 error if the user does not exist
            return await quart.send_file('website/404.html'), 404

class api_routes:
    @staticmethod
    @app.route('/api/status')
    async def index():
        return 'raindrop', 200

    @staticmethod
    @app.route('/api/raindrop-status')
    async def status():
        token = quart.request.args.get('token', None)
        user_restricted = user_login(token=token).is_restricted()

        return {
            "Components": {
                'database': PostgreSQL.check_db_container() if not user_restricted else -1,
                'webui': {
                    'running': webgui.is_running() if not user_restricted else -1,
                    'restricted': False,
                },
                'api': {
                    "running": True,
                    "restricted": user_restricted,
                }
            },
            "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }, 200

    @staticmethod
    @app.route('/api/login', methods=['POST'])
    @QuartAPI.require_json
    async def login():
        data = await quart.request.get_json()
        username = data.get('username', None)
        password = data.get('password', None)

        if not username or not password:
            return {
                'error': 'username and password are required',
                'token': None
            }, 400

        try:
            user = user_login(username=username, password=password)
        except PermissionError:
            return {
                'error': 'Username or password is invalid',
                'token': None
            }, 401
        except error.user_nonexistant:
            return {
                'error': 'User does not exist',
            }, 404
        except Exception as err: # Catch all exceptions
            logging.error(err, exc_info=err.__traceback__)
            return {
                'error': 'An error occurred',
                'token': None
            }, 500

        return {
            "error": None,
            "token": user.generate_token()
        }, 200

    @staticmethod
    @app.route('/api/register', methods=['POST'])
    @QuartAPI.require_json
    async def register():
        data = await quart.request.get_json()
        username = data.get('username', None)
        password = data.get('password', None)

        if not username or not password:
            return {'error': 'username and password are required'}, 400

        try:
            success = users.register(username=username, password=password)
        except error.user_already_exists:
            return {
                'error': 'User already exists',
            }, 409
        return {
            'success': success,
        }, 200 if success else 400

    @staticmethod
    @app.route('/api/validate/<token>', methods=['GET'])
    async def is_valid_token(token):
        is_valid = PostgreSQL().validate_token(token)
        return {
            'valid': is_valid
        }, 200

class vcs_routes:
    @staticmethod
    @app.route('/api/vcs/commits_chart', methods=['POST', 'GET'])
    async def commits_data():
        if quart.request.method == 'POST':
            data = await quart.request.get_json()
            try:
                username = data.get('username', None)
            except AttributeError:
                raise error.json_content_type_only
        else:  # GET request
            username = quart.request.args.get('username', None)

        if type(username) is not str:
            return {
                'error': 'username is required and must be a string',
            }, 400

        # Check if the user exists
        if not username == "*":
            users.exists(username)
        else:
            # If username is "*", return all commits
            pass

        # Test data.
        # TODO: Implement this function to return actual data
        return {
            1: 10,
            2: 20,
            3: 30,
            4: 40,
            5: 287,
            6: 60,
            7: 70,
            8: 80,
            9: 1,
            10: 2,
            11: 91,
            12: 12,
            13: 40,
            14: 21,
        }, 200

    @staticmethod
    @app.route('/api/vcs/repositories/list_private', methods=['GET'])
    @QuartAPI.require_authentication
    async def list_private_repositories(user: user_login):
        return {'private': user.list_private_repos()}, 200

    @staticmethod
    @app.route('/api/vcs/repositories/<username>/list_public', methods=['GET'])
    async def list_public_repositories(username):
        # Ensures the user exists
        if not users.exists(username):
            raise error.user_nonexistant
        return {'public': vcs.list_pub_repositories(username)}, 200

    @staticmethod
    @app.route('/api/vcs/repositories/list_all', methods=['GET'])
    @QuartAPI.require_authentication
    async def list_repositories(user: user_login):
        private_repositories:dict = user.list_private_repos()
        public_repositories:dict = user.list_public_repos()

        return {
            # Format, {repo_name: description}
            'private': private_repositories,
            'public': public_repositories,
        }, 200

    @staticmethod
    @app.route('/api/vcs/repository/create', methods=['POST'])
    @QuartAPI.require_json
    @QuartAPI.require_authentication
    async def create_repository(user: user_login):
        data = await quart.request.get_json()

        repository_name = data.get('repo_name', None)
        description = data.get('description', None)
        is_private = data.get('is_private', True)

        if not repository_name or not description:
            return {
                'error': 'repository_name is required'
            }, 400

        success = user.create_repository(repository_name, description, is_private)
        return {
            'success': success
        }, 200 if success else 400

    @staticmethod
    @app.route('/api/vcs/repository/delete', methods=['POST'])
    @QuartAPI.require_json
    @QuartAPI.require_authentication
    async def delete_repository(user: user_login):
        data = await quart.request.get_json()

        repository_name = data.get('repo_name', None)

        if not repository_name:
            return {
                'error': 'repository_name is required'
            }, 400

        success = user.delete_repository(repository_name)
        return {
            'success': success
        }, 200 if success else 400

    @staticmethod
    @app.route('/api/vcs/repository/exists', methods=['GET'])
    async def repository_exists():
        repo_name = quart.request.args.get('repo_name', None)
        owner = quart.request.args.get('owner', None)

        if not repo_name or not owner:
            return {
                'error': 'repo_name and owner are required'
            }, 400

        exists = vcs.repository_exists(owner, repo_name)
        return {
            'exists': exists
        }, 200

    @staticmethod
    @app.route('/api/vcs/repository/walk', methods=['POST'])
    @QuartAPI.require_json
    async def walk_repository():
        data = await quart.request.get_json()
        repo_owner = data.get('owner', None)
        repo_name = data.get('repo_name', None)

        if not repo_name or not repo_owner:
            return {
                'error': 'repo_name and repo_owner are required'
            }, 400

        # Get the repository handler
        repo = repository_handler(repo_owner, repo_name)
        repo.walk_repo()

class docker_routes:
    @staticmethod
    @app.route('/api/docker/list', methods=['GET'])
    @QuartAPI.require_authentication
    async def list_containers(user: user_login):
        return {
            'containers': user.list_docker_containers()
        }, 200

    @staticmethod
    @app.route('/api/docker/start', methods=['POST'])
    @QuartAPI.require_json
    @QuartAPI.require_authentication
    async def start_container(user: user_login):
        data = await quart.request.get_json()
        container_id = data.get('container_id', None)

        if not container_id:
            return {
                'error': 'container_id is required'
            }, 400

        success:bool = user.start_docker_container(container_id)
        return {
            'success': success
        }, 200 if success else 400

    @staticmethod
    @app.route('/api/docker/stop', methods=['POST'])
    @QuartAPI.require_json
    @QuartAPI.require_authentication
    async def stop_container(user: user_login):
        data = await quart.request.get_json()
        container_id = data.get('container_id', None)

        if not container_id:
            return {
                'error': 'container_id is required'
            }, 400

        success:bool = user.stop_docker_container(container_id)
        return {
            'success': success
        }, 200 if success else 400

    @staticmethod
    @app.route('/api/docker/create', methods=['POST'])
    @QuartAPI.require_json
    @QuartAPI.require_authentication
    async def create_container(user: user_login):
        data = await quart.request.get_json()

        container_name = data.get('name', None)
        container_image = data.get('image', None)
        host_port = data.get('host_port', None)
        internal_port = data.get('internal_port', None)
        host_ip = data.get('host_ip', None)
        host_volume = data.get('host_volume', None)
        internal_volume = data.get('internal_volume', None)

        # Server-side data validation
        # Regex makes sure the name is docker-valid and > 4 and less than < 40 characters
        regex = r'^[a-zA-Z0-9][a-zA-Z0-9_.-]{3,39}$'
        if not re.match(regex, container_name):
            return {
                'error': 'Invalid container name'
            }, 400

        # Check if the image exists
        if not container_image:
            return {
                'error': 'image is required'
            }, 400
        else:
            image_exists = docker_image_exists(image_name=container_image, tag='latest')
            if not image_exists:
                return {
                    'error': 'image does not exist'
                }, 400

        # Check if the ports are valid
        if not host_port or not internal_port:
            return {
                'error': 'host_port and container_port are required'
            }, 400
        elif not isinstance(host_port, int) or not isinstance(internal_port, int):
            return {
                'error': 'host_port and container_port must be integers'
            }, 400

        # Check if the host_ip is valid.
        if host_ip is None or host_ip == '':
            host_ip = '0.0.0.0'
        elif not re.match(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', host_ip):
            return {
                'error': 'Invalid host ip address specified'
            }, 400

        # A Regex to check if the host volume is a valid path for linux and windows
        linux_regex = r'^/([a-zA-Z0-9_-]+/)*[a-zA-Z0-9_-]*/?$'
        windows_regex = r'^[a-zA-Z]:[\\/](?:[^\\/:*?"<>|\r\n]+[\\/])*[^\\/:*?"<>|\r\n]*$'

        if host_volume and internal_volume:
            if not re.match(linux_regex, host_volume) and not re.match(windows_regex, host_volume):
                return {
                    'error': 'Host volume path is invalid on both Linux and Windows'
                }, 400

            if not re.match(linux_regex, internal_volume):
                return {
                    'error': 'Internal volume path is invalid on Linux'
                },

        if host_volume and not internal_volume or internal_volume and not host_volume:
            return {
                'error': 'Both host_volume and internal_volume must be provided'
            }, 400

        success = user.create_docker_container(
            image=container_image,
            name=container_name,
            internal_port=internal_port,
            host_port=host_port,
            host_ip=host_ip,
            host_volume=host_volume,
            internal_volume=internal_volume
        )

        return {
            'success': success
        }, 200 if success else 400

    @staticmethod
    @app.route('/api/docker/delete', methods=['POST'])
    @QuartAPI.require_json
    @QuartAPI.require_authentication
    async def delete_container(user: user_login):
        data = await quart.request.get_json()
        container_id = data.get('container_id', None)

        if not container_id:
            return {
                'error': 'container_id is required'
            }, 400

        success:bool = user.delete_docker_container(container_id)
        return {
            'success': success
        }, 200 if success else 400