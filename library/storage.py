from library.cmd_interface import cli_handler, colours
from library.encryption import encryption
from library.errors import error
import subprocess
import psycopg2
import datetime
import secrets
import inspect
import logging
import time
import json
import os

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s'
)

keys = encryption()
key_seperator = '.'
settings_path = 'settings.json'
DEBUG = os.environ.get('DEBUG', False)

class dt:
    SETTINGS = {
        "_comment": "NEVER SHARE THIS DATA FILE TO ANYONE. DOING SO COULD MEAN BAD THINGS.",
        "hostname": "127.0.0.1",
        'firstlaunch': {
            'main': True
        },
        'webgui': {
            'port': 2048,
            'enabled': True
        },
        'api': {
            'port': 4096,
        },
        'db': {
            'external': False,
            'host': None,
            'port': None,
            'username': None,
            'raindrop_password': None,
            'postgres_password': None,
            'database': None
        }
    }

    REPO_CONFIG = {
        "repo_id": None,
        "version": None,
        "repo_name": None,
        "description": None,
    }


# noinspection DuplicatedCode
class var:
    @staticmethod
    def set(key, value, file=settings_path, dt_default=dt.SETTINGS) -> bool:
        """
        Sets the value of a key in the memory file.

        :param key: The key to set the value of.
        :param value: The value to set the key to.
        :param file: The file to set the key in.
        :param dt_default: The default dictionary to fill a json file with if the file does not exist.
        :return:
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(f'file \'{file}\' was set by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is False:
            os.makedirs(file_dir, exist_ok=True)
            with open(file, 'w+') as f:
                json.dump(dt_default, f, indent=4, separators=(',', ':'))

        with open(file, 'r+') as f:
            data = json.load(f)

        temp = data
        for k in keys[:-1]:
            if k not in temp:
                temp[k] = {}
            temp = temp[k]

        temp[keys[-1]] = value

        with open(file, 'w+') as f:
            json.dump(data, f, indent=4)

        return True

    @staticmethod
    def get(key, default=None, dt_default=dt.SETTINGS, file=settings_path) -> any:
        """
        Gets the value of a key in the memory file.

        :param key: The key to get the value of.
        :param default: The default value to return if the key does not exist.
        :param dt_default: The default dictionary to fill a json file with if the file does not exist.
        :param file: The file to get the key from.
        Set to None if you want to raise an error if the file does not exist.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            caller = f"{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}"
            logging.info(f'file \'{file}\' was retrieved from by {caller}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is True:
            with open(file, 'r+') as f:
                data = dict(json.load(f))
        else:
            if dt_default is not None:
                os.makedirs(file_dir, exist_ok=True)
                with open(file, 'w+') as f:
                    json.dump(dt_default, f, indent=4, separators=(',', ':'))
            else:
                raise FileNotFoundError(f"file '{file}' does not exist.")

            with open(file, 'r+') as f:
                data = dict(json.load(f))

        temp = data
        try:
            for k in keys[:-1]:
                if k not in temp:
                    return default
                temp = temp[k]

            return temp[keys[-1]]
        except KeyError as err:
            logging.error(f"key '{key}' not found in file '{file}'.", err)
            raise KeyError(f"key '{key}' not found in file '{file}'.")

    @staticmethod
    def delete(key, file=settings_path, default=dt.SETTINGS):
        """
        Delete a key.

        :param key: The key to delete.
        :param file: The file to delete the key from.
        :param default: The default dictionary to fill a json file with if the file does not exist.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            caller = f"{inspect.stack()[1].filename}:{inspect.stack()[1].lineno}"
            logging.info(f'file \'{file}\' was had a key deleted by {caller}')

        keys = str(key).split(key_seperator)
        file_dir = os.path.dirname(file)
        if file_dir == '':
            file_dir = os.getcwd()

        if os.path.exists(file) is True:
            with open(file, 'r+') as f:
                data = dict(json.load(f))
        else:
            if default is not None:
                os.makedirs(file_dir, exist_ok=True)
                with open(file, 'w+') as f:
                    json.dump(default, f, indent=4, separators=(',', ':'))
            else:
                raise FileNotFoundError(f"file '{file}' does not exist.")

            with open(file, 'r+') as f:
                data = dict(json.load(f))

        temp = data
        for k in keys[:-1]:
            if k not in temp:
                return False
            temp = temp[k]

        if keys[-1] in temp:
            del temp[keys[-1]]
            with open(file, 'w+') as f:
                json.dump(data, f, indent=4)
            return True
        else:
            return False

    @staticmethod
    def load_all(file: str = settings_path, dt_default={}) -> dict:
        """
        Load all the keys in a file. Returns a dictionary with all the keys.
        :param file: The file to load all the keys from.
        :param dt_default:
        :return:
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(
                f'file \'{file}\' was fully loaded by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        os.makedirs(os.path.dirname(file), exist_ok=True)
        if not os.path.exists(file):
            with open(file, 'w+') as f:
                json.dump(dt_default, f, indent=4, separators=(',', ':'))

        with open(file, 'r+') as f:
            data = dict(json.load(f))

        return data

    @staticmethod
    def fill_json(file: str = settings_path, data=dt.SETTINGS):
        """
        Fill a json file with a dictionary.
        :param file: The file to fill with data.
        :param data: The data to fill the file with.
        """
        # Logs the file it creates, and which file and line called it.
        if DEBUG is True:
            logging.info(
                f'file \'{file}\' was filled with data by {inspect.stack()[1].filename}:{inspect.stack()[1].lineno}')

        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w+') as f:
            json.dump(data, f, indent=4, separators=(',', ':'))

        return True

class postgre_cli:
    def __init__(self):
        self.details = PostgreSQL.get_details()

        self.cli = cli_handler(
            "PostgreSQL",
            greet_func=self.greet_func,
            use_plugins=False
        )

        self.cli.register_command(
            'pair',
            func=self.pair,
            description="Pair with the PostgreSQL database.",
        )

        self.cli.register_command(
            'start',
            func=PostgreSQL.start_db,
            description="Start the PostgreSQL database."
        )

        self.cli.register_command(
            'install',
            func=PostgreSQL.make_db_container,
            description="Install the PostgreSQL database."
        )

        self.cli.register_command(
            'test',
            func=PostgreSQL.ping_db,
            description="Test the connection to the database."
        )

        self.cli.register_command(
            'execute',
            func=self.query_db,
            description="Execute a query on the database."
        )

        self.cli.register_command(
            'reveal',
            func=self.reveal_password,
            description="Reveal the password for the database."
        )

    def main(self):
        self.cli.main()
        return True

    def reveal_password(self):
        print(f"Username: {self.details['user']}")
        print(f"Password: {PostgreSQL.get_details()['password']}")
        return True

    def query_db(self):
        query = self.cli.ask_question("What's the query you want to run?")
        args = ()
        while True:
            try:
                arg = self.cli.ask_question(
                    "What's the argument you want to pass to the query?",
                    exit_notif_msg=" Press Enter with blank input to finish.",
                    default=None,
                    ask_if_valid=True
                )
            except self.cli.exited_questioning:
                break
            if arg is None:
                break
            args += (arg,)

        # Confirm the user wants to run the query and knows the risks.
        attempted_exit = False
        while True:
            print(f"{colours['yellow']}WARNING: Running a query can be very dangerous.")
            print(f"{colours['yellow']}DO NOT RUN QUERIES SENT TO YOU BY OTHERS. This could lead to total loss of data")
            print(f"{colours['yellow']}Only run queries you have written or are sure of as working and safe.")
            if attempted_exit:
                print("Read the warning before continuing.")
            try:
                time.sleep(5)  # Makes the user read the warning
                break
            except (KeyboardInterrupt, Exception):
                continue

        confirmed = self.cli.ask_question(
            "Are you sure you want to run this query? (y/n)",
            options=['y', 'n'], show_options=False,
            default='n'
        )
        if confirmed:
            result = PostgreSQL.query_db(query, args)
            print(result)
            return True
        else:
            print("Query cancelled.")
            return True

    def greet_func(self):
        print(f"Welcome to the {self.cli.cli_name} CLI\n")

        db_status = PostgreSQL.check_db_container()
        if db_status == -1:
            print(f"The PostgreSQL container has not been created.")

        print(f"The database is currently online." if db_status else "The DB is not running.")

    def pair(self):
        while True:
            try:
                db_host = self.cli.ask_question(
                    "What is the Hostname of the PostgreSQL database?",
                    default=self.details.get('host', "127.0.0.1"),
                    filter_func=postgre_cli.filters.db_host
                )
                db_port = self.cli.ask_question(
                    "What is the Port of the PostgreSQL database?",
                    default=5432, filter_func=lambda x: x.isdigit()
                )
                db_username = self.cli.ask_question(
                    "What is the Username of the PostgreSQL database?",
                    default='api-raindrop',
                )
                db_password = self.cli.ask_question(
                    "What is the Password of the PostgreSQL database?",
                    default=var.get('db.raindrop_password'),
                )
                db_database = self.cli.ask_question(
                    "What is the Database of the PostgreSQL database?",
                    default='raindrop',
                )
            except self.cli.exited_questioning:
                print("Exiting pairind mode.")
                return True

            self.details = {
                'host': db_host,
                'port': db_port,
                'username': db_username,
                'password': db_password,
                'database': db_database
            }

            is_external = db_host not in ['localhost', '127.0.0.1']

            print("Attempting to pair...")
            try:
                conn = psycopg2.connect(**self.details)
                conn.close()
                break
            except psycopg2.OperationalError as err:
                logging.error('Could not connect to the database.', err)
                print(f"The database could not be paired.\nError: {err}\n")
                print("Did you enter the correct details?")
                retry = self.cli.ask_question(
                    "Would you like to retry?",
                    options=['y', 'n'],
                    default='n'
                ) == 'y'
                if retry:
                    continue
                else:
                    break

        self.details['username'] = keys.encrypt(self.details['username'])
        self.details['password'] = keys.encrypt(self.details['password'])
        PostgreSQL.save_details(self.details)

        var.set('db.external', is_external)
        return True

    class filters:
        """
        Filters for text-based input.
        """
        @staticmethod
        def db_host(db_host) -> bool:
            if db_host.lower() in ["127.0.0.1", 'localhost'] and var.get('db.external') is True:
                print(f"{colours['red']}Host cannot be '{db_host}' when using an external database.")
                return False

            if db_host == "":
                print(f"{colours['red']}Host cannot be empty.")
                return False

            return True

class PostgreSQL:
    def __init__(self):
        self.details = PostgreSQL.get_details()

        self.cli = postgre_cli()

        # Makes a test connection to the database
        self.ping_db()

    @staticmethod
    def stop_container():
        """
        Stops the PostgreSQL container.
        """
        subprocess.run(
            ["docker", "stop", "raindrop-postgres"],
            check=True,
        )

    def get_connection(self) -> psycopg2.extensions.connection:
        try:
            return psycopg2.connect(**self.details)
        except psycopg2.OperationalError as err:
            # Try to start up the docker container for the database
            if not PostgreSQL.start_db():
                logging.error('Could not reach the database, and when I tried to start the PostgreSQL container, It failed.', exc_info=True)
                raise err

            msg = 'The database is starting up. Please wait.'
            print(msg)
            logging.info(msg)

            # Wait for the database to start up
            time_waited = 0
            while not self.ping_db(do_print=False):
                # If the database does not start up in 10 seconds, raise an error
                if time_waited > 10:
                    logging.error('The database did not start up in time.')
                    raise err
                time_waited += 1
                time.sleep(1)
            return psycopg2.connect(**self.details)

    def ping_db(self, do_print=False):
        try:
            conn = psycopg2.connect(**self.details)
            conn.close()
            if do_print:
                print("The database is online.")
            return True
        except psycopg2.OperationalError as err:
            if do_print:
                print(f"The database is offline. Error: {err}")
            return False

    @staticmethod
    def query_db(query, args, do_commit=True):
        """
        Query the database.
        :param query: The query to run.
        :param args: The arguments to pass to the query.
        :param do_commit: Whether to commit the query.
        :return: The result of the query.
        """
        conn = psycopg2.connect(**PostgreSQL.get_details())
        cur = conn.cursor()
        cur.execute(query, args)
        if do_commit:
            conn.commit()
        result = cur.fetchall()
        conn.close()
        return result

    @staticmethod
    def save_details(details: dict):
        """
        Saves the details of the PostgreSQL database to the secrets file.
        :param details: The details to save.
        """
        var.set(key='db.host', value=details['host'])
        var.set(key='db.port', value=details['port'])
        var.set(key='db.username', value=details['username'])
        var.set(key='db.raindrop_password', value=details['raindrop_password'])
        var.set(key='db.postgres_password', value=details['postgres_password'])
        var.set(key='db.database', value=details['database'])

    @staticmethod
    def start_db() -> bool:
        """
        Starts the PostgreSQL container.
        :return: True if the container was started, False if it was not started.
        """
        if var.get('db.external') is False:
            subprocess.run(
                ["docker", "start", "raindrop-postgres"],
                check=True,
            )
            return True
        else:
            return False

    @staticmethod
    def check_db_container() -> bool | int:
        """
        Checks if the PostgreSQL container exists and is running.
        :return: True if the container is running, False if it is not running, and -1 if it does not exist.
        """
        # Checks if the PostgreSQL container exists and is running
        result = subprocess.run(
            ["docker", "inspect", "--format='{{json .State.Status}}'", "raindrop-postgres"],
            capture_output=True, text=True
        )

        if not var.get("db.external") is True:
            if result.returncode != 0:
                # Container does not exist
                return -1
        else:
            # Makes a test connection to the database
            try:
                conn = psycopg2.connect(**PostgreSQL.get_details())
                conn.close()
            except psycopg2.OperationalError:
                return False
            return True

        status = json.loads(result.stdout.strip().strip("'"))
        if status == "running":
            return True
        else:
            return False

    @staticmethod
    def make_db_container() -> bool:
        # Uses docker to make a PostgreSQL container
        postgres_password = secrets.token_urlsafe(32)

        # Run the Docker container
        try:
            subprocess.run(
                [
                    "docker", "run", "--name", "raindrop-postgres",
                    "-e", f"POSTGRES_PASSWORD={postgres_password}",
                    "-p", "5432:5432",
                    '--restart', 'unless-stopped',
                    "-d", "postgres"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error(f'Could not create the container. {err}', )
            return False

        # Create the PostgreSQL schema/database and user
        try:
            print("Waiting for the DB to start...")
            time.sleep(3)

            subprocess.run(
                [
                    "docker", "exec", "-i", "raindrop-postgres",
                    "psql", "-U", "postgres",
                    "-c", f"CREATE DATABASE raindrop;"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error('Could not create the database on PostgreSQL.', err)
            return False

        try:
            raindrop_password = secrets.token_urlsafe(32)

            subprocess.run(
                [
                    "docker", "exec", "-i", "raindrop-postgres",
                    "psql", "-U", "postgres",
                    "-c", f"CREATE USER raindrop_api WITH PASSWORD '{raindrop_password}';"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error('Could not create the DB user.', err)
            return False

        # Set the password in the secrets file
        PostgreSQL.save_details({
            'host': '127.0.0.1',
            'port': 5432,
            'username': 'raindrop_api',
            'raindrop_password': keys.encrypt(raindrop_password),
            'postgres_password': keys.encrypt(postgres_password),
            'database': 'raindrop'
        })

        try:
            PostgreSQL().grant_all_perms()
        except subprocess.CalledProcessError as err:
            logging.error('Could not grant all permissions to the user.', err)
            return False

        var.set('db.external', False)

        PostgreSQL().modernize()

        return True

    @staticmethod
    def grant_all_perms():
        subprocess.run(
            [
                "docker", "exec", "-i", "raindrop-postgres",
                "psql", "-U", "postgres",
                "-c", "GRANT ALL PRIVILEGES ON DATABASE raindrop TO raindrop_api;"
            ],
            check=True,
        )

    @staticmethod
    def get_details() -> dict:
        return {
            'host': var.get('db.host'),
            'port': var.get('db.port'),
            'user': 'postgres',
            'password': keys.decrypt(var.get('db.postgres_password')),
            'database': var.get('db.database')
        }

    def modernize(self):
        # Fetch a database connection
        conn = self.get_connection()
        cur = conn.cursor()

        # Using this dict, it formats the SQL query to create the tables if they don't exist
        table_dict = {
            'tokens': {
                'username': 'TEXT NOT NULL UNIQUE PRIMARY KEY',
                'token': 'TEXT NOT NULL UNIQUE'
            },
            'accounts': {
                'user_id': 'SERIAL PRIMARY KEY',
                'registered_on': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'username': 'TEXT NOT NULL UNIQUE',
                'password': 'TEXT NOT NULL',
                'restricted': 'BOOLEAN DEFAULT FALSE',
                'bio': 'TEXT DEFAULT \'Feeling new? Make a bio!\'',
            },
            'repositories': {
                'repo_id': 'SERIAL PRIMARY KEY',
                'owner': 'TEXT NOT NULL REFERENCES accounts(username)',
                'name': 'TEXT NOT NULL',
                'description': 'TEXT',
                'private': 'BOOLEAN DEFAULT FALSE',
                'created_on': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
                'last_updated': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            },
            'user_permissions': {
                'username': 'TEXT NOT NULL REFERENCES accounts(username)',
                'administrator': 'BOOLEAN DEFAULT FALSE',
            },
            # The full file is stored in the commits table
            'commits': {
                'commit_id': 'SERIAL PRIMARY KEY',
                'repo_id': 'INTEGER NOT NULL REFERENCES repositories(repo_id)',
                'author': 'TEXT NOT NULL REFERENCES accounts(username)',
                'version_major': 'INTEGER NOT NULL',
                'version_minor': 'INTEGER NOT NULL',
                'version_patch': 'INTEGER NOT NULL',
                'rel_file_path': 'TEXT NOT NULL',  # The relative file path. Eg, '/folder/file.txt' or '/file.txt'
                'file_data': 'TEXT NOT NULL',  # Base64 encoded file data
                'commit_message': 'TEXT NOT NULL DEFAULT \'No message provided\'',
                'commit_date': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
            }
        }

        PostgreSQL.grant_all_perms()

        for table_name, columns in table_dict.items():
            # Check if the table exists
            cur.execute('''
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = %s
                );
            ''', (table_name,))
            table_exist = cur.fetchone()[0]

            # If the table exists, check and update columns
            if table_exist:
                for column_name, column_properties in columns.items():
                    # Check if the column exists
                    cur.execute('''
                        SELECT EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_name = %s AND column_name = %s
                        );
                    ''', (table_name, column_name))
                    column_exist = cur.fetchone()[0]

                    # If the column doesn't exist, add it
                    if not column_exist:
                        cur.execute(f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_properties};')

            # If the table doesn't exist, create it with columns
            else:
                columns_str = ', '.join(
                    [f'{column_name} {column_properties}' for column_name, column_properties in columns.items()]
                )
                try:
                    cur.execute(f'CREATE TABLE {table_name} ({columns_str});')
                except psycopg2.errors.DuplicateTable:
                    continue
                except psycopg2.errors.SyntaxError:
                    logging.info(f"Could not create table '{table_name}'. Query:\n"
                                 f"{f'CREATE TABLE {table_name} ({columns_str});'}")
                    exit(1)
                except psycopg2.errors.InsufficientPrivilege:
                    logging.info("Insufficient privileges to create the table. Exiting.")

        # Commit the changes
        conn.commit()

    def save_token(self, belongs_to, token):
        """
        Saves a token for a user in the database.

        :param belongs_to: The username of the user the token belongs to.
        :type belongs_to: str
        :param token: The token to save.
        :type token: str
        :raises AssertionError: If the username or token is not a string.
        """
        assert type(belongs_to) is str, "The username must be a string."
        assert type(token) is str, "The token must be a string."
        # Check if the user exists
        self.check_exists(belongs_to)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO tokens (username, token)
                VALUES (%s, %s)
                ON CONFLICT (username) DO UPDATE SET token = EXCLUDED.token;
                """,
                (belongs_to, token)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_token_owner(self, token):
        """
        Retrieves the username associated with a given token.

        :param token: The token to look up.
        :type token: str
        :raises AssertionError: If the token is not a string.
        :return: The username associated with the token.
        :rtype: str
        """
        assert type(token) is str, "The token must be a string."
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT username
                FROM tokens
                WHERE token = %s;
                """,
                (token,)
            )
            return cur.fetchone()[0]
        finally:
            cur.close()
            conn.close()

    def validate_token(self, token):
        """
        Validates if the provided token exists in the database.

        :param token: The token to validate.
        :type token: str
        :raises AssertionError: If the token is not a string.
        :return: True if the token is valid, False otherwise.
        :rtype: bool
        """
        assert type(token) is str, "The token must be a string."
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT username
                FROM tokens
                WHERE token = %s;
                """,
                (token,)
            )
            valid = cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()
        return valid

    def walk_repository(self, repo_name, repo_owner, view_private=False):
        """
        Constructs a dictionary of all the files, their versions, their commit msg, and their relative paths.
        :param repo_name: The name of the repository.
        :param repo_owner: The owner of the repository.
        :param view_private: Whether to view private repositories.
        :return:
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT version_major, version_minor, version_patch, rel_file_path, commit_message
                FROM commits
                WHERE repo_id = (
                    SELECT repo_id
                    FROM repositories
                    WHERE name = %s AND owner = %s{';' if view_private else ' AND private = FALSE;'}
                );
                """,
                (repo_name, repo_owner)
            )
            files = cur.fetchall()
        finally:
            cur.close()
            conn.close()

        files_dict = {}
        for file in files:
            version = [file[0], file[1], file[2]]
            rel_file_path = file[3]
            commit_msg = file[4]
            files_dict[rel_file_path] = {
                'version': version,
                'commit_msg': commit_msg
            }

        return files_dict

    # TODO: Add a way for admins to create an account for a user without the user's input
    def add_user(self, username: str, password: str):
        """
        Adds a new user to the database.

        :param username: The username of the new user.
        :type username: str
        :param password: The password for the new user.
        :type password: str
        :raises AssertionError: If the username or password is not a string.
        :return: True if the user was added successfully, False if the username already exists.
        :rtype: bool
        """
        assert type(username) is str, "The username must be a string."
        assert type(password) is str, "The password must be a string."
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO accounts (username, password)
                VALUES (%s, %s)
                """,
                (username, password)
            )
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            return False
        finally:
            cur.close()
            conn.close()
        return True

    # TODO: Add way for user to trigger the deletion of their account
    def delete_user(self, username: str):
        """
        Deletes a user from the database.

        :param username: The username of the user to delete.
        :type username: str
        :raises AssertionError: If the username is not a string.
        """
        assert type(username) is str, "The username must be a string."

        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                DELETE FROM accounts
                WHERE username = %s;
                """,
                (username,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_repository_owner(self, repo_name, hide_private=True):
        """
        Retrieves the owner of a repository.

        :param repo_name: The name of the repository.
        :type repo_name: str
        :param hide_private: If True, only considers public repositories.
        :type hide_private: bool
        :return: The owner of the repository.
        :rtype: str
        """
        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT owner
                FROM repositories
                WHERE name = %s{';' if not hide_private else ' AND private = FALSE;'}
                """,
                (repo_name,)
            )
            owner = cur.fetchone()[0]
        finally:
            cur.close()
            conn.close()
        return owner

    def check_exists(self, username:str, not_exist_ok=False):
        """
        Checks if a user exists in the database.
        :param username: The username to check.
        :param not_exist_ok: If True, does not raise an error if the user does not exist.
        :return:
        """
        conn = self.get_connection()
        cur = conn.cursor()

        assert type(username) is str, "The username must be a string."

        try:
            # Check if the owner exists
            cur.execute(
                """
                SELECT username
                FROM accounts
                WHERE username = %s;
                """,
                (username,)
            )
            exists = cur.fetchone() is not None
        finally:
            cur.close()
            conn.close()

        if not exists:
            if not_exist_ok is False:
                raise error.user_nonexistant
            else:
                return False
        else:
            return True

    def is_user_administrator(self, username:str):
        """
        Checks if a user is an administrator.
        :param username: The username to check.
        :return: True if the user is an administrator, False otherwise.
        """
        # Check if the user exists
        assert type(username) is str, "The username must be a string."
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT administrator
                FROM user_permissions
                WHERE username = %s;
                """,
                (username,)
            )
            is_admin = cur.fetchone()[0]
        # Excepts for when the user is not in the user_permissions table
        except (TypeError, IndexError):
            return False
        finally:
            cur.close()
            conn.close()

        return is_admin

    # TODO: Add way for user to change password
    def update_password(self, username:str, password:str):
        """
        Updates the password of a user.
        :param username: The username of the user.
        :param password: The new password.
        :return:
        """
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE accounts
                SET password = %s
                WHERE username = %s;
                """,
                (password, username)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_password(self, username:str):
        """
        Retrieves the password of a user.
        :param username: The username of the user.
        :return:
        """
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT password
                FROM accounts
                WHERE username = %s;
                """,
                (username,)
            )
            password = cur.fetchone()
            if password is None:
                return None
            return password[0]
        finally:
            cur.close()
            conn.close()

    # TODO: Allow user to access this feature
    def set_bio(self, username, bio):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE accounts
                SET bio = %s
                WHERE username = %s;
                """,
                (bio, username)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def get_bio(self, username):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT bio
                FROM accounts
                WHERE username = %s;
                """,
                (username,)
            )
            bio = cur.fetchone()
            if bio is None:
                return None
            return bio[0]
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for administrator to restrict users from using the service
    def is_restricted(self, username):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT restricted
                FROM accounts
                WHERE username = %s;
                """,
                (username,)
            )
            restricted = cur.fetchone()
            if restricted is None:
                return None
            return restricted[0]
        finally:
            cur.close()
            conn.close()

    def set_restricted(self, username, new_status:bool):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                UPDATE accounts
                SET restricted = %s
                WHERE username = %s;
                """,
                (new_status, username)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to make users an administrator
    def make_user_administrator(self, username):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO user_permissions (username, administrator)
                VALUES (%s, TRUE)
                ON CONFLICT (username) DO UPDATE SET administrator = TRUE;
                """,
                (username,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to remove users as administrators
    def remove_user_administrator(self, username):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO user_permissions (username, administrator)
                VALUES (%s, FALSE)
                ON CONFLICT (username) DO UPDATE SET administrator = FALSE;
                """,
                (username,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to trigger the creation of a repository
    def add_repository(self, owner:str, name:str, description:str, is_private:bool):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**self.get_details())
        cur = conn.cursor()

        assert isinstance(is_private, bool)
        assert isinstance(name, str)
        assert isinstance(description, str)
        assert isinstance(owner, str)

        # Check if the owner exists
        self.check_exists(owner)

        # Insert the new repository
        try:
            cur.execute(
                """
                INSERT INTO repositories (owner, name, description, private)
                VALUES (%s, %s, %s, %s);
                """,
                (owner, name, description, is_private)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to trigger the deletion of a repository
    def delete_repository(self, owner:str, name:str):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**self.get_details())
        cur = conn.cursor()

        assert isinstance(name, str)
        assert isinstance(owner, str)

        # Check if the owner exists
        self.check_exists(owner)

        try:
            # Delete all commits associated with the repository
            cur.execute(
                """
                DELETE FROM commits
                WHERE repo_id = (
                    SELECT repo_id
                    FROM repositories
                    WHERE owner = %s AND name = %s
                );
                """,
                (owner, name)
            )

            # Delete the repository
            cur.execute(
                """
                DELETE FROM repositories
                WHERE owner = %s AND name = %s;
                """,
                (owner, name)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to trigger updating if its private or not
    def update_repository_is_private(self, owner, name, is_private):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**self.get_details())
        cur = conn.cursor()

        assert isinstance(is_private, bool)
        assert isinstance(name, str)
        assert isinstance(owner, str)

        # Check if the owner exists
        self.check_exists(owner)

        # Update the repository
        try:
            cur.execute(
                """
                UPDATE repositories
                SET private = %s
                WHERE owner = %s AND name = %s;
                """,
                (is_private, owner, name,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to trigger updating the name of the repository
    def update_repository_name(self, owner, old_name, new_name):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**self.get_details())
        cur = conn.cursor()

        assert isinstance(new_name, str)
        assert isinstance(old_name, str)
        assert isinstance(owner, str)

        # Check if the owner exists
        self.check_exists(owner)

        # Update the repository
        try:
            cur.execute(
                """
                UPDATE repositories
                SET name = %s
                WHERE owner = %s AND name = %s;
                """,
                (new_name, owner, old_name,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    # TODO: Add way for user to trigger updating the description of the repository
    def update_repository_description(self, owner, name, description):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**self.get_details())
        cur = conn.cursor()

        assert isinstance(description, str)
        assert isinstance(name, str)
        assert isinstance(owner, str)

        # Check if the owner exists
        self.check_exists(owner)

        # Update the repository
        try:
            cur.execute(
                """
                UPDATE repositories
                SET description = %s
                WHERE owner = %s AND name = %s;
                """,
                (description, owner, name,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    @staticmethod
    def sort_to_dict(cursor):
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, item)) for item in cursor.fetchall()]

    def list_public_repos(self, username):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            # Execute the query to get repository data
            cur.execute(
                """
                SELECT *
                FROM repositories
                WHERE owner = %s AND private = FALSE;
                """,
                (username,)
            )

            return PostgreSQL.sort_to_dict(cur)
        finally:
            cur.close()
            conn.close()

    def list_private_repos(self, username):
        # Check if the user exists
        self.check_exists(username)

        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT repo_id, name, description, owner, created_on, last_updated, private
                FROM repositories
                WHERE owner = %s AND private = TRUE;
                """,
                (username,)
            )

            # Return the data and sort it into a dictionary
            return PostgreSQL.sort_to_dict(cur)
        finally:
            cur.close()
            conn.close()

    def get_repo(self, owner, name):
        # Check if the user exists
        self.check_exists(owner)

        conn = self.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """
                SELECT repo_id, name, description, owner, created_on, last_updated, private
                FROM repositories
                WHERE owner = %s AND name = %s;
                """,
                (owner, name)
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
