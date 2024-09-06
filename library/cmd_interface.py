from difflib import get_close_matches
from colorama import Fore, Style
from typing import List
import importlib.util
import platform
import colorama
import datetime
import logging
import os

os.makedirs('logs/', exist_ok=True)

DEBUG = os.environ.get('RD_DEBUG', False)
colorama.init(autoreset=True)

logging.basicConfig(
    filename=f'logs/{datetime.datetime.now().strftime("%Y-%m-%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s'
)

colours = {
    'red': Fore.RED,
    'green': Fore.GREEN,
    'yellow': Fore.YELLOW,
    'blue': Fore.BLUE,
    'purple': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE,
    'end': Style.RESET_ALL
}


# noinspection PyMethodMayBeStatic
class cli_handler:
    def __init__(
            self,
            cli_name: str,
            greet_func=None,
            use_default_cmds=True,
            use_plugins=False,
            plugins_dir='plugins',
            is_main_cli=False,
    ):
        """
        Initialises the CLI handler.

        :param cli_name: The name to print in the CLI input section. eg, "TutoringFlow".
        :param greet_func: The function to call to greet the user each loop through the CLI. eg, "Welcome to the CLI."
        :param use_default_cmds: If True, uses the default commands. eg, help, exit, cls.
        :param use_plugins: If True, uses the plugins in the plugins directory.
        :param plugins_dir: The directory to look for plugins in.
        :param is_main_cli: If True, this is the main CLI. If False, this is a sub-CLI.
        """
        self.greet_func = greet_func
        self.cli_name = cli_name
        self.cmds_dict = {}
        self.registered_commands = {}
        self.use_plugins = use_plugins
        self.is_main_cli = is_main_cli
        self.running = True
        self.plugins_dir = plugins_dir

        if use_default_cmds:
            # Sets up the default commands as registered cmds and cmd_dict entries.
            self.register_command(
                cmd='help',
                func=self.help_cmd,
                description='Get help with all available commands.',
                args=[],
                func_args=None,
            )

            if use_plugins:
                self.cmds_dict['help']['plugins'] = {}
            self.register_command(
                cmd='exit',
                func=self.exit,
                description='Exits the CLI.',
                args=[],
                func_args=None
            )

            # Register the clear command with aliases (way of doing it without extra code. Will do properly one day)
            for alias in ['cls', 'clear']:
                self.register_command(
                    cmd=alias,
                    func=self.clear_terminal,
                    description='Clears the terminal screen.',
                    args=[],
                    func_args=None
                )

            # Load plugins last
            if use_plugins:
                os.makedirs(self.plugins_dir, exist_ok=True)
                self.load_plugins_from(self.plugins_dir)
        else:
            # Why I have made it even possible to disable this, I have no idea. It shouldn't be possible.
            logging.warning(
                "Default commands are disabled.\n"
                "You must register your own commands, including exit.\n"
                "This has not been tested in the slightest because I am sane enough to not disable this.\n"
            )

        # Looks in the args of each command to see how many args it can take. Counts the max.
        max_args_possible = 0
        for cmd in self.cmds_dict:
            if len(self.cmds_dict[cmd]['args']) > max_args_possible:
                max_args_possible = len(self.cmds_dict[cmd]['args'])

        self.max_args = max_args_possible

    def exit(self):
        """
        Exits the CLI.
        """
        if self.is_main_cli:
            raise KeyboardInterrupt
        else:
            self.running = False
            return True

    def clear_terminal(self):
        """
        Clears the terminal screen.
        """
        print("If you can see this, it means your terminal does not support clearing the screen.")
        print("So here is a bunch of new lines instead.")
        for i in range(100):
            print("\n")
        os.system('cls' if os.name == 'nt' else 'clear')
        return True

    def load_plugin(self, plugin_file_dir: str, class_name: str) -> bool:
        """
        Load a singular plugin, a python file, from a directory.
        It grabs the plugin by file and class name.

        The class must have a method called 'main'. This is the method that will be called when the command is executed.
        The class must also have a method called 'help' for its help command.
        Missing these methods will cause the plugin to not be loaded.

        The plugin name should be put in a file called 'plugin' with no extension on line 1.
        On line 2, the plugins description should be put. Line breaks indicated by \n

        The class name should always be the same as the file name

        All other python files a plugin should need should be in a subdirectory.
        The main plugin file should be in the same directory as 'plugin' config file

        in the plugins folder in the plugins directory.
        This name will be used by the CLI for the user to execute 'main' and 'help' command.

        It is recommended a plugin creates another instance of the cli_handler class to register its commands.

        :param plugin_file_dir: The directory of the plugin.
        :param class_name: The name of the class to load.
        """
        try:
            # Convert the file path to module path
            spec = importlib.util.spec_from_file_location(class_name, plugin_file_dir)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)

            # Get the class from the module
            plugin_class = getattr(plugin_module, class_name)
            plugin_instance = plugin_class()  # Instantiate the class

            # Get the functions 'main' and 'help' from the instance
            main_func = getattr(plugin_instance, 'main', None)
            help_func = getattr(plugin_instance, 'help', None)

            # Ensure they are valid
            if not callable(main_func) or not callable(help_func):
                raise AttributeError("The plugin class must have callable 'main' and 'help' methods.")

            # Load plugin name and description
            with open(os.path.join(os.path.dirname(plugin_file_dir), 'plugin'), 'r') as f:
                plugin_name = f.readline().strip()
                plugin_desc = f.readline().strip()

            if " " in plugin_name:
                raise ValueError("Plugin name cannot have spaces.")

            # Register commands and help
            self.register_command(
                cmd=plugin_name,
                func=main_func,
                description=plugin_desc,
                args=[],
                func_args=None
            )
            self.register_plugin_help_func(plugin_name, help_func)

            return True
        except (ImportError, AttributeError, ValueError, FileNotFoundError) as err:
            logging.error(f"Error loading plugin: {err}", err)

        return False

    def load_plugins_from(self, plugin_dir: str) -> bool:
        assert os.path.isdir(plugin_dir), "Plugin directory does not exist."
        for plugin in os.listdir(plugin_dir):
            if os.path.isdir(f"{plugin_dir}/{plugin}"):
                # Finds any file that ends with .py in the dir
                python_file = [f for f in os.listdir(f"{plugin_dir}/{plugin}") if f.endswith('.py')][0]

                # Load the absolute path of the plugin
                self.load_plugin(os.path.abspath(f"{plugin_dir}/{plugin}/{python_file}"), plugin)
        return True

    def register_plugin_help_func(self, plugin_name: str, help_func) -> bool:
        """
        Registers a help function for a plugin.

        :param plugin_name: The name of the plugin to register the help function for.
        :param help_func: The help function to register.
        :return: True if the help function was registered successfully.
        """
        self.cmds_dict["help"]["plugins"][plugin_name] = help_func
        self.cmds_dict["help"]["args"].append(plugin_name)
        self.registered_commands["help"]["uses_args"] = True
        return True

    def find_similar(self, cmd: str, cmd_args: list, ask_to_execute=False) -> dict | None:
        """
        Finds commands and args that are similar to the one the user entered.
        Used to help the user if they mistype a command.

        :param cmd: The command to find similar commands to.
        :param ask_to_execute: If True, asks the user if they want to execute the similar command or not.
        :param cmd_args: The arguments of the command.
        :return: The list of similar commands or None if the user doesn't want to execute them or there are none similar
        """
        try:
            similar_cmd = get_close_matches(
                word=cmd,
                possibilities=self.cmds_dict.keys(),
            )[0]
        except IndexError:
            return None

        if cmd_args is None:
            cmd_args = []

        if cmd_args is not None:
            if len(cmd_args) > 0:
                possible_args = self.cmds_dict[similar_cmd]['args']
                similar_args = []
                for i in range(len(cmd_args)):
                    # Finds the similar args for the similar command.
                    try:
                        similar_args.append(get_close_matches(
                            word=cmd_args[i],
                            possibilities=possible_args
                        )[0])
                    except IndexError:
                        continue

                cmd_args = similar_args

        logging.info(
             f'User entered an invalid command: \"{cmd}\".'
             f'(ask if should execute: {ask_to_execute}) Found similar command: \"{similar_cmd}\".'
        )
        if not ask_to_execute:
            return {'cmd': similar_cmd, 'args': cmd_args}
        else:
            try:
                facsimile_cmd = f"{similar_cmd} {' '.join(cmd_args)}".strip()
            except TypeError:
                facsimile_cmd = similar_cmd  # just use the command. (cmd args are None on type error)
            print(
                f"{colours['yellow']}Did you mean{colours['white']}: {colours['green']}\"{facsimile_cmd}\"?"
                f"(*y/n)"
            )
            response = input('>>> ').lower()
            if response not in ['n', 'no']:
                logging.info(f'User chose to execute the similar command: \"{similar_cmd}\".')
                return {'cmd': similar_cmd, 'args': cmd_args}
            else:
                logging.info(f'User did not execute the similar command: \"{similar_cmd}\".')
                return None

    def ask_question(
            self,
            question: str,
            options: List[str] = [],
            exit_phrase='exit',
            confirm_validity=True,
            ask_if_valid=False,
            default=None,
            show_default: bool = True,
            filter_func=None,
            colour='green',
            allow_default: bool = True,
            show_options: bool = True,
            exit_notif_msg: str = "default",
            clear_terminal: bool = True
    ) -> str:
        """
        Asks the user a question and returns the answer.

        :param question:
        :param options: The list of acceptable answers.
        :param exit_phrase: The phrase to type to exit the question.
        :param confirm_validity: Determines if the answer must be in the options list and toggles filter_func.
        :param ask_if_valid: Asks the user if the answer is correct.
        :param default: The default answer to return if the user enters nothing.
        :param show_default: If True, shows the default answer in the prompt.
        :param filter_func: A function to filter the answer. (can be anything)
        Have it return False if the answer is bad and -1 if the answer is bad but the user shouldn't be told.
        Return true if the answer is good.
        :param colour: The colour of the prompt. eg, "red" or "green".
        :param allow_default: If True, allows the default answer to be returned.
        :param show_options: If True, shows the options list.
        :param exit_notif_msg: The message to indicate how to exit questioning.
        :param clear_terminal: If True, clears the terminal before asking the question.
        :return: The answer to the question.
        :raises: self.exited_question if the user exits the question.
        """
        # Call validation
        assert type(options) is list, f"options must be a list, not {type(options)}"
        if len(options) > 0:
            for option in options:
                assert type(option) is str, f"options must be a list of strings, not {type(option)}"
        assert type(question) is str, f"question must be a string, not {type(question)}"
        assert type(exit_phrase) is str and exit_phrase != "", "exit_phrase must be a non-empty string."
        assert type(confirm_validity) is bool, f"confirm_validity must be a boolean. Not {type(confirm_validity)}"
        assert type(ask_if_valid) is bool, f"ask_if_valid must be a boolean. Not {type(ask_if_valid)}"
        assert default is not callable, f"default must not be a callable. It is {type(default)}"
        assert type(colour) is str, f"colour must be a string. Not {type(colour)}"
        assert type(allow_default) is bool, f"allow_default must be a boolean. Not {type(allow_default)}"
        assert type(show_options) is bool, f"show_options must be a boolean. Not {type(show_options)}"
        assert type(clear_terminal) is bool, f"clear_terminal must be a boolean. Not {type(clear_terminal)}"

        # Doing it like this since the f-string doesn't work in the args
        if exit_notif_msg == "default":
            exit_notif_msg = f" | Type '{exit_phrase}' to exit."

        try:
            if clear_terminal:
                self.clear_terminal()
            while True:
                if show_options and len(options) > 0:
                    print("\n")
                    for option in options:
                        print(f"- {colours['yellow']}{option}")
                    print("(Acceptable answers above)")
                print(f"{question}{exit_notif_msg}")
                answer = input(f"{colours[colour]}{f'({default}) ' if show_default else ''}>>> ")

                # Handles specific inputs, eg, exit phrase
                if answer == "":
                    if allow_default:
                        answer = default
                if answer == exit_phrase:
                    raise self.exited_questioning

                # Check if the answer is valid
                if confirm_validity:
                    if len(options) > 0 and answer not in options:
                        print(f"{colours['red']}Invalid input.")
                        continue
                    if filter_func is not None:
                        filter_result = filter_func(answer)
                        if filter_result is False:
                            print(f"{colours['red']}That input was filtered as bad.")
                            continue
                        elif filter_result == -1:
                            # -1 is for a bad input that should be filtered but not told to the user.
                            # Eg, if the filter func tells them why it's bad itself.
                            continue

                if ask_if_valid:
                    print(f"{colours['yellow']}You entered: {answer}. Is this correct? (y/n)")
                    response = input(">>> ").lower()
                    if response not in ['y', 'yes']:
                        continue

                return answer
        except KeyboardInterrupt:
            raise self.exited_questioning

    class exited_questioning(Exception):
        def __init__(self):
            super().__init__("User cancelled the question and answer session.")

    def list_commands(self, return_only=False):
        """
        Lists all commands that the user can use in the CLI.

        :param return_only: If True, returns the dictionary of commands.
        :return: The dictionary of commands.
        """
        if return_only:
            return self.cmds_dict
        else:
            for cmd, desc in self.cmds_dict.items():
                cmd_has_args = len(desc['args']) != 0
                if cmd_has_args:
                    args_msg = f"\nParameters: {', '.join(desc['args'])}"
                else:
                    args_msg = "\nNo parameters."
                print(f"- {cmd}: {desc['msg']}{args_msg}\n")
            try:
                if self.use_plugins:
                    print("Plugin help commands:")
                    for plugin_name in self.cmds_dict['help']['plugins']:
                        print(f"- help {plugin_name}")
            except KeyboardInterrupt:
                pass
            return True

    def help_cmd(self, args=None):
        """
        The help command. Lists all available commands or shows help for a specific plugin.
        """
        if args:
            if args[0] in self.cmds_dict.get('help', {}).get('plugins', {}):
                # Show help for the specific plugin
                plugin_name = args[0]
                help_func = self.cmds_dict['help']['plugins'][plugin_name]
                help_func()  # Call the plugin's help function
            return True
        else:
            # Show help for all commands
            self.list_commands()
            try:
                input("Press enter to continue.")
                return True
            except KeyboardInterrupt:
                return True

    def register_command(self, cmd:str, func, description='', args:list=[], func_args:tuple=None) -> bool:
        """
        Registers a command with its corresponding function.

        :param cmd: The command to register.
        :param func: The function to execute when the command is called.
        :param func_args: The arguments that the function takes.
        :param description: Description of the command.
        :param args: List of potential arguments for the command.

        :return: True if the command was registered successfully.

        The difference between args and func_args is that args is a list of potential 'sub-commands' for the command.
        For example, say you have a 'makeHome' command, arg 0 could be 'private' or 'public'. and function to make it so
        but func_args is the arguments that the function takes. It'd be called like any python func would be with those
        args.
        """
        cmd = cmd.lower()
        self.registered_commands[cmd] = {}
        self.registered_commands[cmd]['func'] = func
        self.registered_commands[cmd]['uses_args'] = func_args is not None
        self.registered_commands[cmd]['args'] = func_args
        self.cmds_dict[cmd] = {'msg': description, 'args': args}
        return True

    def main(self):
        """
        Handles the command line interface. Not only that, but it is also useful for development to
        make functions available and callable BEFORE designing their web interface.
        :return:
        """
        executing_similar = (False, None, None)
        logging.info("TF CLI has been called.")
        try:
            # Captures current terminal text and puts it in a variable
            if DEBUG is True:
                print(f"NOTICE: {self.cli_name} CLI is in Debug Mode")

            try:
                while self.running:
                    if not executing_similar[0]:
                        if self.greet_func is not None:
                            self.greet_func()
                        else:
                            print(f"Welcome to the {self.cli_name} CLI.")
                            print("Type 'help' for a list of commands.")
                        prompt = input(f"{colours['green']}{self.cli_name}{colours['end']}> ").lower()
                        prompt_split = prompt.split(" ")
                        # Takes all the arguments after the command and puts them in a list
                        args = prompt_split[1:] if len(prompt_split) > 1 else None
                        cmd = prompt_split[0]
                    else:
                        cmd = executing_similar[1]
                        args = executing_similar[2]
                        executing_similar = (False, None, None)

                    if DEBUG == 'True':
                        logging.debug(f'User input: {cmd}')
                        logging.debug(f'Arguments: {args}')

                    max_args_possible = self.max_args
                    # If there are no args, pad the list with None.
                    if max_args_possible > 0 and args:
                        if len(args) < max_args_possible:
                            # noinspection PyTypeChecker
                            args.extend([None] * (max_args_possible - len(args)))

                    if args and len(args) > max_args_possible:
                        print(f"{colours['red']}Too many arguments.")
                        logging.warning(f"Too many arguments: {args}")
                        continue

                    if cmd == "":
                        run_success = True
                    elif cmd == "debug":
                        print("DEBUG VALUES:")
                        print(f"DEBUG: {DEBUG}")
                        print(f"Operating System: {platform.platform()}")
                        print(f"Python Version: {platform.python_version()}")
                        run_success = True
                    else:
                        # Try to execute a registered command
                        if cmd in self.registered_commands:
                            if self.registered_commands[cmd]['uses_args'] is True:
                                run_success = self.registered_commands[cmd]['func'](args)
                            else:
                                run_success = self.registered_commands[cmd]['func']()

                            if DEBUG:
                                print(f"Command returned: {run_success}")
                                logging.debug(f"Command returned: {run_success}")

                            if not isinstance(run_success, bool):
                                logging.warning(f"Command did not return a boolean value: {run_success}")
                                print(f"{colours['yellow']}Command \"{cmd}\" did not return a success boolean value.")
                                print(f"So we do not know if the command worked.")
                                run_success = True
                        else:
                            run_success = False

                    # Acts as an Else block. If a sub-command is not found, will now fall here.
                    if run_success is not True:
                        print(f"{colours['red']}Error: Command not found.")
                        logging.debug(f"Command not found: {cmd}")
                        similar = self.find_similar(cmd, ask_to_execute=True, cmd_args=args)
                        if similar is not None:
                            executing_similar = (True, similar['cmd'], similar['args'])
                            continue

                    executing_similar = (False, None, None)  # Reset the tuple just in case.

                # The below code only runs if this is a sub-CLI, Otherwise it runs the keyboard interrupt code.
                if not self.is_main_cli:
                    print(f"{colours['red']}Returning to main CLI...")
                    return True
            except AssertionError as err:
                print(f"{colours['red']}{err}")
                logging.error(f"Assertion Error: {err}")
        except KeyboardInterrupt:
            print(f"{colours['red']}Exiting...")
            logging.info(f"User exited the '{self.cli_name}' CLI.")
            exit(0)
