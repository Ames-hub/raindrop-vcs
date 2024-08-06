from library.versioncontrolsystem import versionControlSystem
from library.storage import var, PostgreSQL
from library.userman import userman
from library.webui import webgui
import quart_cors
import datetime
import uvicorn
import quart
import os

os.makedirs('data/users/', exist_ok=True)

# Specify the path to the templates directory
template_dir = os.path.join(os.getcwd(), 'website/templates')

app = quart.Quart(__name__, template_folder=template_dir)
quart_cors.cors(app, allow_origin='*')

class QuartAPI:
    @staticmethod
    def run():
        uvicorn.run(
            app,
            host='0.0.0.0',
            port=var.get('api.port'),
        )

@app.route('/api')
async def index():
    return 'raindrop', 200
@app.route('/api/raindrop-status')
async def status():
    token = quart.request.args.get('token', None)
    user_restricted = userman(token=token).is_restricted()

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

@app.route('/vcs/commits_chart', methods=['POST', 'GET'])
async def commits_data():
    if quart.request.method == 'POST':
        data = await quart.request.get_json()
        username = data.get('username', None)
    else:  # GET request
        username = quart.request.args.get('username', None)

    if not username:
        return {'error': 'Username is required'}, 400

    # If username is "*": return all commits

    # Process the username as needed
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

@app.route('/view/<username>', methods=['GET', 'POST'])
async def get_account(username):
    user = userman(username)

    if quart.request.method == 'GET':
        if user.exists():
            return await quart.render_template(
                template_name_or_list='account.html',
                username=username,
                pfp_address=user.get_pfp_address(),
                banner_address=user.get_banner_address(),
                user_bio=user.get_bio(),
            ), 200
        else:
            # Responds with a 404 error if the user does not exist
            return await quart.send_file('website/404.html'), 404
    else:  # POST request
        # Return if the user exists
        return {'exists': user.exists()}, 200

@app.route('/view/<username>/pfp', methods=['GET'])
async def get_pfp(username):
    pfp: str = userman(username).get_pfp(dir_only=True)
    print(pfp)
    return await quart.send_file(pfp), 200

@app.route('/view/<username>/banner', methods=['GET'])
async def get_banner(username):
    banner_data = userman(username).get_banner(dir_only=True)
    return await quart.send_file(banner_data), 200

@app.route('/view/<username>/bio', methods=['GET'])
async def get_bio(username):
    return userman(username).get_bio(), 200

@app.route('/view/<username>/repository/list', methods=['GET'])
async def list_repositories(username):
    if not username:
        return {'error': 'username is required'}, 400
    else:
        assert type(username) is str, 'username must be a string.'
        return {'repos_list': userman(username).list_repositories()}, 200

@app.route('/view/<account>/<repository>', methods=['GET'])
async def get_repository(account, repository):
    repo = versionControlSystem(account, repository)

    if repo.exists():
        return await quart.render_template(
            'repository.html',
            username=account,
            repo_name=repository,
            version=repo.version
        )
    else:
        return await quart.send_file('website/404.html'), 404

@app.route('/vcs/repository/init', methods=['POST'])
async def init_repository():
    data = await quart.request.get_json()
    token = data.get('token', None)
    repository = data.get('repository', None)
    description = data.get('description', None)

    if not token or not repository:
        return {'error': 'token and repository are required.'}, 400

    repo = versionControlSystem(token=token, repo_id=repository)

    if repo.exists():
        return {'error': 'Repository already exists.', 'success': False}, 400
    else:
        repo.init_repo(
            description=description)
        return {'success': True}, 200

@app.route('/vcs/repository/dir', methods=['POST'])
async def dirlist_repository():
    data = await quart.request.get_json()
    account = data.get('account', None)
    repository = data.get('repository', None)
    if not account or not repository:
        return {'error': 'Account and repository are required.'}, 400

    repo = versionControlSystem(account, repository)

    if repo.exists():
        return repo.walk(), 200
    else:
        return {'directories': {}}, 404

@app.route('/vcs/repository/src', methods=['GET'])
async def vcs_pull(account, repository):
    repo = versionControlSystem(account, repository)

    data = await quart.request.get_json()
    requested_version = data.get('version', 'latest')
    requested_file = os.path.join(
        "repositories",
        account,
        repository,
        data.get('reldir', None),
    )

    if repo.exists():
        return repo.pull(requested_file, requested_version), 200
