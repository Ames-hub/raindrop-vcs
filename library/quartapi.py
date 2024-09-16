from library.versioncontrolsystem import repository_handler, vcs
from library.user_login import user_login, users
from library.storage import var, PostgreSQL
from library.webui import webgui
from library.errors import error
import quart_cors
import functools
import datetime
import uvicorn
import logging
import quart
import os

os.makedirs('data/users/', exist_ok=True)

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s'
)

# Specify the path to the templates directory
template_dir = os.path.join(os.getcwd(), 'website/templates')

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

class QuartAPI:
    @staticmethod
    def run():
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=var.get('api.port'),
        )

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
            username = data.get('username', None)
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
    @QuartAPI.require_authentication
    async def delete_repository(user: user_login):
        data = await quart.request.get_json()

        repository_name = data.get('repo_name', None)

        if not repository_name:
            return {
                'error': 'repository_name is required'
            }, 400

        # TODO: Implement this function
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
