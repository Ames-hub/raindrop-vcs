from library.storage import var, PostgreSQL, postgre_cli
from library.cmd_interface import cli_handler, colours
from library.quartapi import QuartAPI
from library.webui import webgui
from library.pylog import pylog
import multiprocessing
import dotenv
import time
import os

dotenv.load_dotenv('secrets.env')
logging = pylog(use_latestlog=True,)

if __name__ == '__main__':
    logging.start_logging()

cli = cli_handler(
    'Raindrop',
    is_main_cli=True,
    use_default_cmds=True,
    use_plugins=True
)

class raindrop:
    @staticmethod
    def main():
        if var.get('firstlaunch.main'):
            raindrop.setup()
        webui_installed = webgui.docker_test()
        if not webui_installed:
            print(f"{colours['yellow']}The WebUI is not installed. Raindrop can only function as an API due to this.")

        # Start the API
        API_Process = multiprocessing.Process(
            target=QuartAPI.run,
            name='API',
        )
        API_Process.start()

        cli.register_command(
            cmd='webui',
            func=webgui.cli.main,
            description='Manage the WebUI container'
        )

        cli.main()

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
    def setup():
        print(f"{colours['green']}Welcome to Raindrop!{colours['white']}")
        print("Since this is your first time running Raindrop VCS Server, we need to set up a few things.\n")
        advanced_mode = cli.ask_question(
            "Do you want to the advanced setup mode? (y/n)",
            options=['y', 'n'],
            default='n', show_options=False
        ) == 'y'

        try:
            while raindrop.docker_test(True) != 0:
                print(f"{colours['red']}Docker is not installed. Please install Docker to run Raindrop.")
                time.sleep(10)
            input("Has docker been setup? If not, please set it up fully now. (Press enter to continue)")
        except KeyboardInterrupt:
            print(f"\n{colours['red']}Exiting setup.")
            exit(1)

        # Try to install the webgui Nginx container
        install_webui = cli.ask_question(
            "Raindrop is mainly a WebUI app. Regardless, it can function as simply an API.\n"
            "Do you want to install the WebUI? (y/n)",
            default='y',
            confirm_validity=False
        ).lower()

        if install_webui:
            print("Installing the WebUI container...")
            if advanced_mode:
                use_default = cli.ask_question(
                    "Do you want to use the default port for the WebUI? (y/n)",
                    filter_func=lambda x: x.lower() == 'y' or x.lower() == 'n',
                    default='y'
                )
                if not use_default:
                    port = cli.ask_question(
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
            use_default = cli.ask_question(
                "Do you want to use the default port for the API? (y/n)",
                filter_func=lambda x: x.lower() == 'y' or x.lower() == 'n',
                default='y'
            ) == 'y'

            if not use_default:
                api_port = cli.ask_question(
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
                    use_lanloopback = cli.ask_question(
                        f"{colours['yellow']}Warning: Using 'localhost' or '127.0.0.1' as the hostname"
                        f" will make the API only accessible from the local machine.",
                        options=['ok', 'cancel'],
                        default='ok'
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
        hostname = cli.ask_question(
            "What is the hostname of the server?\n"
            "The hostname is the IP address or domain name of the server.\n"
            "eg, '192.168.1.114 or 'google.com'",
            filter_func=_filter_func,
            default="127.0.0.1",
        )
        var.set('api.hostname', hostname)

        # Setup DB Credentials and container if needed
        while not os.path.exists('secrets.env'):  # Retry logic.
            existing_db = cli.ask_question(
                "A PostgreSQL database is required for Raindrop to function.\n"
                "Do you have an existing PostgreSQL database you wish to use? (y/n)",
                options=['y', 'n'],
                default='n'
            ) == 'y'

            if existing_db is False:
                make_new_db = cli.ask_question(
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
                    db_make_success = PostgreSQL.make_db_container()
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

        var.set('firstlaunch.main', False)
        print(f"{colours['green']}Setup complete!{colours['end']}")
        return True


if __name__ == '__main__':
    raindrop.main()