from library.cmd_interface import cli_handler
from library.storage import var
from library.pylog import pylog
import subprocess
import os

logging = pylog()

class webgui:
    @staticmethod
    def docker_test() -> bool:
        """
        Tests to see if the WebUI on docker is installed
        :return: True if installed, False if not
        """
        # Gets all the docker containers
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'], capture_output=True, text=True)
        if 'raindrop-webui' in result.stdout:
            installed = True
        else:
            installed = False

        return installed

    @staticmethod
    def install(for_CLI=False) -> bool:
        """
        Install the webgui as a docker container named "raindrop-webui"
        """
        if for_CLI:
            print("Installing the WebUI container now...")

        # Create the docker client
        os.system('docker pull nginx')

        content_dir = os.path.join(os.getcwd(), 'website\\')
        os.makedirs(content_dir, exist_ok=True)

        config_file = os.path.join(os.getcwd(), 'nginx.conf')

        if not os.path.exists(config_file):
            logging.warning(f"Config file 'nginx.conf' does not exist in the project directory.")
            return False

        port: int = var.get('webgui.port')

        # Check if the "raindrop-webui" container already exists
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=raindrop-webui', '--format', '{{.Names}}'],
                                capture_output=True, text=True)
        if 'raindrop-webui' in result.stdout:
            print("Docker container 'raindrop-webui' already exists. Cannot proceed.")
        else:
            # Container doesn't exist, create it
            docker_command = [
                'docker', 'run', '-d', '--name', 'raindrop-webui',
                '-p', f'0.0.0.0:{port}:80', '-v', f'{content_dir}:/usr/share/nginx/html',
                '-v', f'{config_file}:/etc/nginx/conf.d/default.conf',
                '--restart', 'unless-stopped', 'nginx'
            ]
            try:
                subprocess.run(docker_command)
            except Exception as err:
                logging.error(f"Failed to create the 'raindrop-webui' container.", err)
                return False

        if for_CLI:
            print("WebUI container has been installed and is now running if all went as planned.")

        return True

    @staticmethod
    def is_running():
        """
        Check if the WebUI container is running
        :return: True if running, False if not
        """
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True)
        if 'raindrop-webui' in result.stdout:
            return True
        else:
            return False

    class cli:
        @staticmethod
        def main():
            """
            Enter the WebUI CLI
            """
            webui_cli = cli_handler(cli_name='WebUI', greet_func=webgui.cli.greet_func)

            webui_cli.register_command(
                cmd='setup',
                func=webgui.install,
                func_args=[True],
                description='Install the WebUI container'
            )

            webui_cli.main()

            # Must return True to indicate to the main CLI that the command has finished
            return True

        @staticmethod
        def greet_func():
            print("Welcome to the WebUI CLI!")
            # Checks if the webui container 'raindrop-webui' is running and prints the status
            if webgui.is_running():
                print("The WebUI container is currently running.")
            else:
                if webgui.docker_test() is False:
                    print("The WebUI container is not installed. Enter 'setup' to install it.")
                else:
                    print("The WebUI container is not currently running.")

            print("Type 'help' for a list of commands, and type 'exit' to return to the main CLI.")
