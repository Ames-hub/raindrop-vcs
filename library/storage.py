from library.cmd_interface import cli_handler, colours
from library.pylog import pylog
import subprocess
import psycopg2
import secrets
import inspect
import dotenv
import time
import json
import os

logging = pylog()
key_seperator = '.'
settings_path = 'settings.json'
dotenv.load_dotenv('secret.env')
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
            'password': None,
            'database': None
        }
    }

    REPO_CONFIG = {
        "name": None,
        "version": None,
        "description": None,
    }

    USER_CONFIG = {
        'username': None,
        'password': None,
        'bio': None,
        'restricted': False,  # Whether the user is restricted from accessing Raindrop and the API
    }

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
        )

        self.cli.register_command(
            'pair',
            func=self.pair,
        )

        self.cli.register_command(
            'start',
            func=PostgreSQL.start_db,
        )

        self.cli.register_command(
            'install',
            func=PostgreSQL.make_db_container
        )

        self.cli.register_command(
            'test',
            func=PostgreSQL.ping_db
        )

        self.cli.register_command(
            'execute',
            func=self.query_db()
        )

    def main(self):
        self.cli.main()
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
            except self.cli.exited_question:
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
        print(f"Welcome to the Raindrop-PostgreSQL CLI\n")

        db_status = PostgreSQL.check_db_container()
        if db_status == -1:
            print(f"The PostgreSQL container has not been created.")

        print(f"The database is currently online." if db_status else "The DB is not running.")

    def pair(self):
        while True:
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
        var.set(key='db.password', value=details['password'])
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
            logging.error('Could not create the container.', err)
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

            raindrop_password = secrets.token_urlsafe(32)

            subprocess.run(
                [
                    "docker", "exec", "-i", "raindrop-postgres",
                    "psql", "-U", "postgres",
                    "-c", f"CREATE USER raindrop_api WITH PASSWORD '{raindrop_password}';"
                ],
                check=True,
            )
            subprocess.run(
                [
                    "docker", "exec", "-i", "raindrop-postgres",
                    "psql", "-U", "postgres",
                    "-c", "GRANT ALL PRIVILEGES ON DATABASE raindrop TO raindrop_api;"
                ],
                check=True,
            )
        except subprocess.CalledProcessError as err:
            logging.error('Could not create either the database on PostgreSQL or user.', err)
            return False

        # Set the password in the secrets file
        with open('secret.env', 'a+') as f:
            f.write(f"RAINDROP_PASSWORD={raindrop_password}\n")
            f.write(f"POSTGRE_PASSWORD={postgres_password}\n")
            f.write(f"POSTGRE_DATABASE=raindrop\n")
            f.write(f"POSTGRE_USER=raindrop_api\n")
            f.write(f"POSTGRE_HOST=0.0.0.0\n")
            f.write(f"POSTGRE_PORT=5432\n")

        var.set('db.external', False)
        return True

    @staticmethod
    def get_details() -> dict:
        return {
            'host': os.environ.get('POSTGRE_HOST'),
            'port': os.environ.get('POSTGRE_PORT'),
            'user': os.environ.get('POSTGRE_USER'),
            'password': os.environ.get('POSTGRE_PASSWORD'),
            'database': os.environ.get('POSTGRE_DATABASE')
        }

    def modernize(self):
        # Fetch a database connection
        conn = psycopg2.connect(**self.details)
        cur = conn.cursor()

        # Using this dict, it formats the SQL query to create the tables if they don't exist
        table_dict = {
            # Table name
            'tokens': {
                # Column name: Column properties
                'username': 'NOT NULL UNIQUE PRIMARY KEY',
                'token': 'NOT NULL UNIQUE'
            }
        }

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
                cur.execute(f'CREATE TABLE {table_name} ({columns_str});')

        # Commit the changes
        conn.commit()

    def save_token(self, belongs_to, token):
        conn = psycopg2.connect(**self.details)
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
