from library.storage import var, PostgreSQL, postgre_cli
from library.cmd_interface import cli_handler, colours
from library.dvcs import vmsystem, VCS
from library.encryption import encryption
from library.quartapi import QuartAPI
from library.user_login import users
from library.webui import webgui
import multiprocessing
import datetime
import logging
import dotenv
import random
import time
import os

dotenv.load_dotenv('secrets.env')

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s'
)

keys = encryption()

class rd_settings:
    def __init__(self):
        self.settings_cli = cli_handler(
            'RDSettings',
            is_main_cli=False
        )

        self.settings_cli.register_command(
            cmd='fbtoggles',
            description='Toggle the fallbacks',
            func=self.fallbacks_toggle().settings_cli.main,
        )

    class fallbacks_toggle:
        def __init__(self):
            self.settings_cli = cli_handler(
                'FallbacksToggle',
                is_main_cli=False,
                greet_func=self.greeting,
            )

            self.settings_cli.register_command(
                cmd='fallback_db',
                description='Toggle the local DB fallback',
                func=self.toggle_fallback_db,
            )

        @staticmethod
        def greeting():
            allow_local_db: bool = var.get('fallbacks.allow_local_db', default=False)
            if allow_local_db:
                print(f"{colours['green']}Local DB fallback is enabled.")
            else:
                print(f"{colours['red']}Local DB fallback is disabled.")

            print("Toggle the system fallbacks here. Type 'help' for a list of commands.")

        @staticmethod
        def toggle_fallback_db():
            status: bool = var.get('fallbacks.allow_local_db', default=False)
            if status:
                print(f"{colours['yellow']}Disabling local DB fallback...")
                var.set('fallbacks.allow_local_db', False)
            else:
                print(f"{colours['green']}Enabling local DB fallback...")
                var.set('fallbacks.allow_local_db', True)

            return True

class raindrop:
    def __init__(self):
        self.cli = cli_handler(
            'Raindrop',
            is_main_cli=True,
            use_default_cmds=True,
            use_plugins=True
        )

    def main(self):
        if var.get('firstlaunch.main'):
            self.setup()

        # Create the data folder and the users folder if it doesn't exist
        os.makedirs(f'data/vcs/', exist_ok=True)

        # Check if Docker is installed
        raindrop.docker_test(False)

        webui_installed = webgui.docker_test()
        if not webui_installed:
            print(f"{colours['yellow']}The WebUI is not installed. Raindrop can only function as an API due to this.")
        else:
            if var.get('webgui.enabled', default=True):
                if not webgui.is_running():
                    print("WebUI is not running. Starting the WebUI container...")
                    webgui.start_container()
                    print(f"WebUI is online and can be accessed at: {webgui.get_url()}")
                else:
                    print(f"WebUI is online and can be accessed at: {webgui.get_url()}")
            else:
                print(f"{colours['yellow']}The WebUI is not enabled. Raindrop can only function as an API due to this.")

        # Ensures the DB Is running
        if not PostgreSQL().check_db_container():
            print("PostgreSQL is not running. Starting the PostgreSQL container...")
            PostgreSQL().start_db()

            # Modernize DB
            PostgreSQL().modernize()

        # Start the API
        API_Process = multiprocessing.Process(
            target=QuartAPI.run,
            name='API',
        )
        API_Process.start()

        # Note: Yes, apparently this code is neccesary for visuals and shouldn't be changed like how I tried.
        # Checks if the API is Actually running
        while True:
            try:
                time.sleep(1)
                if API_Process.is_alive():
                    print("WebAPI started and is now live and accessible.")
                    break
            except KeyboardInterrupt:
                exit(1)

        self.cli.register_command(
            cmd='webui',
            func=webgui.cli.main,
            description='Manage the WebUI container'
        )

        self.cli.register_command(
            cmd='postgre',
            description='Enter the PostgreSQL CLI',
            func=postgre_cli().main,
            aliases=['pg', 'db', 'database', 'postgres', 'postgresql', 'storage', 'dbcli'],
        )

        self.cli.register_command(
            cmd='versioning',
            description='Manage the version control system',
            func=vmsystem.cli,
            aliases=['vs', 'versioncontrol', 'versioncontrolsystem', 'vcs', 'vc'],
        )

        self.cli.register_command(
            cmd='rcs',
            aliases=['repocontrol', 'repocontrolsystem', 'rc'],
            description='Create, delete, and generally manage repositories',
            func=VCS.cli,
        )

        self.cli.register_command(
            cmd='reveal_sys_pass',
            description='Reveal the system raindrop account password',
            func=self.reveal_sys_pass,
        )

        self.cli.register_command(
            cmd='rd_settings',
            description='Manage Raindrop settings',
            func=rd_settings().settings_cli.main,
            aliases=['settings', 'rdsettings', 'rds', 'raindropsettings', 'raindrop_settings'],
        )

        PostgreSQL().modernize()

        # Checks to make sure the System account (raindrop) exists
        if not PostgreSQL().check_user_exists('Raindrop', not_exist_ok=True):
            print("The system account 'Raindrop' does not exist. Creating the account now...")
            sys_pass = var.get('system.password')
            if not sys_pass is str or not sys_pass is bytes:
                sys_pass = self.cli.ask_question(
                    question="The system password is not set. Please set the system password now.",
                    filter_func=lambda password: password != '' and password is not None and len(password) > 8,
                    confirm_validity=True,
                    default=str(random.randint(100000000000000, 999999999999999))
                )

                sys_pass = keys.encrypt(sys_pass)
                var.set('system.password', sys_pass)

            success = users.register(
                username="Raindrop",
                password=keys.decrypt(sys_pass),
            )
            if success:
                print("The system account 'Raindrop' has been created.")
            else:
                print("Failed to create the system account 'Raindrop'.\n"
                      "Some features may not work as intended.\n"
                      "Please debug this issue to ensure the system account is created, or create it manually. (see 'docs/sys_acc.md')")

        try:
            if var.get('cli_enabled', default=True):
                self.cli.main()
            else:
                print(f"{colours['yellow']}The CLI is disabled in the settings.")
                while True:
                    pass  # Keeps the program running
        except KeyboardInterrupt:
            # Runs clean up code
            print(f"{colours['red']}Exiting Raindrop and running clean up code.")
            webgui.stop_container()
            PostgreSQL.stop_container()
            return True

    @staticmethod
    def docker_test(return_only):
        """
        Tests to see if docker is installed
        :param return_only:
        :return:
        """
        # Routes the terminal output to nowhere for the os.system command
        if os.name != "nt":
            docker_installed = os.system('docker -v > /dev/null 2>&1')
        else:
            docker_installed = os.system('docker -v > NUL 2>&1')

        if return_only:
            return docker_installed

        if docker_installed != 0:
            msg = "Docker is not installed. Please install Docker to run Raindrop."
            logging.info(msg)
            print(msg)
            exit(1)

    @staticmethod
    def reveal_sys_pass():
        """
        Reveals the system password
        :return:
        """
        sys_pass = var.get('system.password')
        if sys_pass is None:
            print("The system password is not set.")
            return False

        sys_pass = keys.decrypt(sys_pass)
        print(f"The system password is: {sys_pass}")
        return True

    def setup(self):
        print(f"{colours['green']}Welcome to Raindrop!{colours['white']}")
        print("Since this is your first time running Raindrop VCS Server, we need to set up a few things.\n")
        try:
            advanced_mode = self.cli.ask_question(
                "Do you want to the advanced setup mode? (y/n)",
                options=['y', 'n'],
                default='n', show_options=False
            ) == 'y'
        except self.cli.exited_questioning:
            print("Exiting setup.")
            exit(0)

        try:
            while raindrop.docker_test(True) != 0:
                print(f"{colours['red']}Docker is not installed. Please install Docker to run Raindrop.")
                time.sleep(10)
            input("Has docker been setup? If not, please set it up fully now. (Press enter to continue)")
        except KeyboardInterrupt:
            print(f"\n{colours['red']}Exiting setup.")
            exit(1)

        # Try to install the webgui Nginx container
        install_webui = self.cli.ask_question(
            "Raindrop is mainly a WebUI app. Regardless, it can function as simply an API.\n"
            "Do you want to install the WebUI? (y/n)",
            default='y',
            confirm_validity=False
        ).lower()

        if install_webui:
            print("Installing the WebUI container...")
            if advanced_mode:
                use_default = self.cli.ask_question(
                    "Do you want to use the default port for the WebUI? (y/n)",
                    filter_func=lambda x: x.lower() == 'y' or x.lower() == 'n',
                    default='y'
                )
                if not use_default:
                    port = self.cli.ask_question(
                        "Enter the port you want to use for the WebUI",
                        filter_func=lambda x: x.isdigit(),
                        default='2048'
                    )
                    var.set('webui.port', port)

            installed = webgui.install()
            if not installed:
                print(
                    f"{colours['red']}Failed to install the WebUI."
                    f"In the project's 'docs' folder, please see 'webui.md' for manual installation instructions."
                )
            else:
                print(f"{colours['green']}WebUI installed successfully!{colours['end']}")

        if advanced_mode:
            use_default = self.cli.ask_question(
                "Do you want to use the default port for the API? (y/n)",
                filter_func=lambda x: x.lower() == 'y' or x.lower() == 'n',
                default='y'
            ) == 'y'

            if not use_default:
                api_port = self.cli.ask_question(
                    "Enter the port you want to use for the API",
                    filter_func=lambda x: x.isdigit(),
                    default=4096
                )
                var.set('api.port', api_port)

        def _filter_func(hostname):
            if hostname == '':
                return False

            while True:
                if hostname in ['localhost', '127.0.0.1']:
                    use_lanloopback = self.cli.ask_question(
                        f"{colours['yellow']}Warning: Using 'localhost' or '127.0.0.1' as the hostname"
                        f" will make the API only usable/accessible from the local machine.",
                        options=['ok', 'cancel'],
                        default='ok',
                        exit_notif_msg=""
                    )
                    if use_lanloopback == 'cancel':
                        print("Let's try that again.")
                        time.sleep(2)
                        return -1
                    else:
                        break
                else:
                    break

            return True

        # While true is Retry logic
        hostname = self.cli.ask_question(
            "What is the hostname of the server?\n"
            "The hostname is the IP address or domain name of the server.\n"
            "eg, '192.168.1.114 or 'google.com'",
            filter_func=_filter_func,
            default="127.0.0.1",
        )
        var.set('api.hostname', hostname)

        # Setup DB Credentials and container if needed
        while not os.path.exists('secrets.env'):  # Retry logic.
            existing_db = self.cli.ask_question(
                "A PostgreSQL database is required for Raindrop to function.\n"
                "Do you have an existing PostgreSQL database you wish to use? (y/n)",
                options=['y', 'n'],
                default='n'
            ) == 'y'

            if existing_db is False:
                make_new_db = self.cli.ask_question(
                    "Do you want to create a new PostgreSQL database container?",
                    options=['y', 'n'], show_options=False,
                    default='y'
                )
                db_msg = ("\nThe creation was cancellled.n\n"
                          "PostgreSQL is required for Raindrop to function.\n"
                          "For setup instructions, see 'docs/postgre.md'")
                if make_new_db:
                    logging.info("The user has chosen to create a new PostgreSQL database container.")
                    print("We are now creating a new PostgreSQL database container for you.")
                    db_make_success = PostgreSQL.make_rd_db_container()
                    if db_make_success is False:
                        print(db_msg)
                        exit(1)
                    else:
                        print("Database container created successfully!")
                else:
                    logging.info("The user has chosen not to create a new PostgreSQL database container.")
                    print(db_msg)
                    exit(1)

                logging.info("The user has completed the setup process.")
                break
            else:
                logging.info("The user has chosen to use an existing PostgreSQL database.")
                print("Entering DB pairing/setup.")
                postgre_cli().pair()

        while True:
            print(f"{colours['red']}!!! IMPORTANT SECURITY NOTICE !!!")
            print(f"{colours['yellow']}NEVER HAND OUT THE FILE 'settings.json', 'secrets.env', AND ESPECIALLY 'private.key' TO ANYONE!")
            print(f"{colours['yellow']}THESE FILES CONTAIN SENSITIVE INFORMATION THAT CAN BE USED TO ACCESS YOUR DATABASE AND API WITHOUT YOUR PERMISSION!")
            does_understand = self.cli.ask_question(
                question="Do you understand? (y/n)",
                options=['yes', 'y', 'no', 'n'],
                default='yes',
                show_options=False,
                clear_terminal=False
            ) in ['yes', 'y']
            if not does_understand:
                print("In that case, please read the message again, and keep doing so until you understand.")
                print("You may have to look up what the files do and why they are important or look up a word you don't understand.")
                time.sleep(2)
            else:
                break

        var.set('firstlaunch.main', False)

        print(f"{colours['green']}Setup complete!{colours['end']}")
        return True


if __name__ == '__main__':
    raindrop().main()
    print("Thank you for using Raindrop!")
    exit(0)