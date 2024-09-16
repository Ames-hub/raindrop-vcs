from difflib import get_close_matches
from colorama import Fore, Style
from typing import List
import importlib.util
import threading
import platform
import colorama
import datetime
import logging
import time
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
        self.running_threads = []

        if use_default_cmds:
            # Sets up the default commands as registered cmds and cmd_dict entries.
            self.register_command(
                cmd='help',
                func=self.help_cmd,
                description='Get help with all available commands.',
                options={},
                func_args=None,
            )

            if use_plugins:
                self.cmds_dict['help']['plugins'] = {}
            self.register_command(
                cmd='exit',
                func=self.exit,
                description='Exits the CLI.',
                options={},
                func_args=None
            )

            self.register_command(
                cmd="cls",
                aliases=["clear", "clearscreen"],
                func=self.clear_terminal,
                description='Clears the terminal screen.',
                options={},
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
            if len(self.cmds_dict[cmd]['options']) > max_args_possible:
                max_args_possible = len(self.cmds_dict[cmd]['options'])

    def exit(self):
        """
        Exits the CLI.
        """
        if self.is_main_cli:
            self.running = False
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
            # Load the module
            plugin_module = importlib.util.module_from_spec(spec)
            # Execute the module
            spec.loader.exec_module(plugin_module)

            # Get the class from the module
            try:
                plugin_class = getattr(plugin_module, class_name)
            except AttributeError:
                raise AttributeError(f"Class {class_name} not found in plugin file '{plugin_file_dir}'.")
            plugin_instance = plugin_class()  # Instantiate the class

            # Get the functions 'main' and 'help' from the instance
            main_func = getattr(plugin_instance, 'main', None)
            help_func = getattr(plugin_instance, 'help', None)

            # Ensure they are valid
            if not callable(main_func) or not callable(help_func):
                raise AttributeError("The plugin class must have callable 'main' and 'help' methods.")

            # Load plugin name and description
            keyvals = self.plugin_config_loadkeys(plugin_file_dir)
            plugin_name = keyvals['name']
            plugin_desc = keyvals['description']
            do_pass_cmd = keyvals.get('do_pass_cmd', False)
            func_args = keyvals.get('func_args', None)
            options = {'args': keyvals.get('options', {}), 'kwargs': keyvals.get('kw_options', {})}
            cmd_aliases:list = keyvals.get('aliases', [])
            auto_task_timer:int = keyvals.get('auto_task_timer', -1)

            # Check if the plugin has an automatic task to run
            if int(auto_task_timer) != -1:
                automated_task = getattr(plugin_instance, 'automatic', None)
                if not callable(automated_task):
                    raise AttributeError("The plugin class must have a callable 'automatic' method if 'auto_task_timer' is set.")
                try:
                    if auto_task_timer < 0.1:
                        raise ValueError("auto_task_timer must be greater than 0.1")
                except ValueError:
                    raise ValueError("auto_task_timer must be an integer.")

                def task_worker():
                    while self.running:
                        automated_task()
                        try:
                            time.sleep(auto_task_timer)
                        except:
                            break

                # Register the automated task to run every x seconds as a threading thread if it does not already exist.
                # Prevents double-ups.
                if not plugin_file_dir in self.running_threads:
                    task_thread = threading.Thread(target=task_worker, name=plugin_file_dir, daemon=True)
                    self.running_threads.append(plugin_file_dir)
                    task_thread.start()

            if " " in plugin_name:
                raise ValueError("Plugin name cannot have spaces.")

            # Register commands and help
            self.register_command(
                cmd=plugin_name,
                func=main_func,
                description=plugin_desc,
                options=options,
                func_args=func_args,
                aliases=cmd_aliases,
                do_pass_cmd=do_pass_cmd
            )
            self.register_plugin_help_func(plugin_name, help_func)

            return True
        except (ImportError, AttributeError, ValueError, FileNotFoundError) as err:
            logging.error(f"Error loading plugin: {err}", exc_info=True)

        return False

    def plugin_config_loadkeys(self, plugin_dir) -> dict:
        """
        Loads the keys from the plugin config file.
        """
        with open(f"{os.path.join(plugin_dir, '..')}/plugin.cf", "r") as plugin_config:
            file = plugin_config.readlines()

        valid_keys = [
            "name",
            "description",
            "aliases",  # example: myplugin,theplugin,plugin
            "do_pass_cmd",  # Whether to pass the full prompt to the CLI to the plugin. Default is False.
            "func_args",  # This isn't too helpful. Will be removed in the future.
            "options",  # example: the command may be "example_plugin now", where "now" is an option.
            'kw_options',  # example: time_to_wait-INT,
            "expected_options_only",  # example: True
            "auto_task_timer",  # example: 20 (seconds)
        ]
        keyvals = {}
        for line in file:
            key = line.split("=")[0]
            value = line.split("=")[1].strip()

            if key not in valid_keys:
                logging.warning(f"Invalid key in plugin config file: {key}")
                continue

            if key in ["aliases", "options"]:
                value = value.split(",")
            elif key == "do_pass_cmd" or key == "expected_options_only":
                value = bool(value)
            elif key == "func_args":
                value = tuple(value.split(","))
            elif key == "kw_options":
                kw_options = value.split(",")
                # kw_v = keyword-value
                for kw_v in kw_options:
                    kw_v = kw_v.split("-")
                    try:
                        option_key = kw_v[0]
                        option_type = kw_v[1]
                    except:
                        logging.error(
                            f"Invalid key-value pair in plugin config file: {kw_v}\n"
                            "Do you have a trailing comma that isn't meant to be there?",
                            exc_info=True
                        )
                        continue
                    value = {option_key: option_type}

            keyvals[key] = value

        return keyvals

    def load_plugins_from(self, plugins_root_dir: str) -> bool:
        """
        Load all plugins from a directory.
        :param plugins_root_dir:
        :return:
        """
        if not os.path.isdir(plugins_root_dir):
            print("Plugin directory does not exist.")
            return False
        for plugin_dir in os.listdir(plugins_root_dir):
            if os.path.isdir(f"{plugins_root_dir}/{plugin_dir}"):
                # Find any file with the .py extension in the plugins directory, and select the first one.
                python_file = [file for file in os.listdir(f"{plugins_root_dir}/{plugin_dir}") if file.endswith(".py")][0]

                # Load the absolute path of the plugin
                self.load_plugin(
                    plugin_file_dir=os.path.abspath(f"{plugins_root_dir}/{plugin_dir}/{python_file}"),
                    class_name=plugin_dir.replace(".py", "")
                )
        return True

    def register_plugin_help_func(self, plugin_name: str, help_func) -> bool:
        """
        Registers a help function for a plugin.

        :param plugin_name: The name of the plugin to register the help function for.
        :param help_func: The help function to register.
        :return: True if the help function was registered successfully.
        """
        self.cmds_dict["help"]["plugins"][plugin_name] = help_func
        self.cmds_dict["help"]["options"]["args"].append(plugin_name)
        self.registered_commands["help"]["uses_args"] = True
        return True

    def find_similar(self, cmd: str, cmd_args: list, ask_to_execute=False) -> dict | None:
        """
        Finds commands and args that are similar to the one the user entered.
        Used to help the user if they mistype a command.

        :param cmd: The command to find similar commands to.
        :param cmd_args: The arguments of the command.
        :param ask_to_execute: If True, asks the user if they want to execute the similar command or not.
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
                possible_args = self.cmds_dict[similar_cmd]['options']
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
            return {'cmd': similar_cmd, 'options': cmd_args}
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
                return {'cmd': similar_cmd, 'options': cmd_args}
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
                cmd_has_args = len(desc['options']) != 0
                if cmd_has_args:
                    args_msg = f"\nParameters: {', '.join(desc['options'])}"
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

    def help_cmd(self, options:dict):
        """
        The help command. Lists all available commands or shows help for a specific plugin.
        """
        if options.get('args', -1) != -1 and len(options.get("args", [])) > 0:
            if options['args'][0] in self.cmds_dict.get('help').get('plugins'):
                # Show help for the specific plugin
                plugin_name = options['args'][0]
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

    def register_command(self, cmd:str, func, description='', options:dict={}, expected_options_only:bool=False,
                         func_args:tuple=None, aliases:list=[], do_pass_cmd:bool=False) -> bool:
        """
        Registers a command with its corresponding function.

        :param cmd: The command to register.
        :param func: The function to execute when the command is called.
        :param func_args: The arguments that the function takes.
        :param description: Description of the command.
        :param options: List of potential arguments for the command.
        :param expected_options_only: If True, the command only accepts the options in the options list.
        :param aliases: List of aliases for the command.
        :param do_pass_cmd: If True, passes the specific command typed to the function.

        :return: True if the command was registered successfully.

        The difference between args and func_args is that args is a list of potential 'sub-commands' for the command.
        For example, say you have a 'makeHome' command, arg 0 could be 'private' or 'public'. and function to make it so
        but func_args is the arguments that the function takes. It'd be called like any python func would be with those
        args.
        """
        assert type(cmd) is str, f"cmd must be a string, not {type(cmd)}"
        assert callable(func), f"func must be a callable, not {type(func)}"
        assert type(description) is str, f"description must be a string, not {type(description)}"
        assert type(options) is dict, f"options must be a dictionary, not {type(options)}"
        assert type(expected_options_only) is bool, f"expected_options_only must be a boolean, not {type(expected_options_only)}"
        assert type(func_args) is tuple or func_args is None, f"func_args must be a tuple or None, not {type(func_args)}"
        assert type(aliases) is list, f"aliases must be a list, not {type(aliases)}"
        assert type(do_pass_cmd) is bool, f"do_pass_cmd must be a boolean, not {type(do_pass_cmd)}"

        # Ensures the options dict is valid.
        if options.get('args', None) is not None:
            for option in options['args']:
                if not isinstance(option, str):
                    print(f"options must be a list of strings, not \"{type(option)}\"")
                    return False
        else:
            options['args'] = []

        if options.get('kwargs', {}) != {}:
            for key in options['kwargs']:
                expected_type = options['kwargs'][key]
                if not isinstance(key, str):
                    print(f"options keys must be strings, not \"{type(key)}\"")
                    return False
                if not expected_type.lower() in ["int", "str", "bool"]:
                    print(f"options values must be types, eg 'INT', 'STR', 'BOOL', not \"{str(expected_type)}\"")
                    return False
                else:
                    expected_type = expected_type.lower()
                    options['kwargs'][key] = expected_type
                    if expected_type == "int":
                        options['kwargs'][key] = int
                    elif expected_type == "str":
                        options['kwargs'][key] = str
                    elif expected_type == "bool":
                        options['kwargs'][key] = bool

        cmd = cmd.lower()
        self.registered_commands[cmd] = {}
        self.registered_commands[cmd]['func'] = func
        self.registered_commands[cmd]['aliases'] = aliases
        self.registered_commands[cmd]['expected_options_only'] = expected_options_only
        self.registered_commands[cmd]['uses_args'] = options != {}
        self.registered_commands[cmd]['args'] = func_args
        self.registered_commands[cmd]['do_pass_cmd'] = do_pass_cmd
        self.cmds_dict[cmd] = {'msg': description, 'options': options}
        return True

    def is_alias(self, possible_alias: str) -> bool:
        """
        Checks if a command is an alias for another command.

        :param possible_alias: The command to check.
        :return: True if the command is an alias for another command.
        """
        for command in self.cmds_dict:
            if possible_alias.lower() in self.registered_commands[command]['aliases']:
                return True
        return False

    def return_alias_origin(self, alias: str) -> str | None:
        """
        Returns the original command as a string that an alias is an alias for.

        :param alias: The alias to check.
        :return: The original command that the alias is an alias for.
        """
        for command in self.cmds_dict:
            if alias in self.registered_commands[command]['aliases']:
                return command
        return None

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
                    options = {'args': [], 'kwargs': {}}
                    if not executing_similar[0]:
                        if self.greet_func is not None:
                            self.greet_func()
                        else:
                            print(f"Welcome to the {self.cli_name} CLI.")
                            print("Type 'help' for a list of commands.")
                        prompt = input(f"{colours['green']}{self.cli_name}{colours['end']}> ").lower()
                        # Assosciates key-value with the args as they are passed in like "cmd key=value" or "cmd key="spaces and value"
                        # takes the prompt and removes the command and preserves the rest of the string as a string
                        try:
                            args_passed = " ".join(prompt.split(" ")[1:])
                        except IndexError:
                            args_passed = ""
                        if len(args_passed) > 0:
                            # splits the args into key-value pairs
                            for arg in args_passed.split(" "):
                                # Handles Kwarg style args
                                if "=" in arg:
                                    key = arg.split("=")[0]
                                    # Finds the index of the key in the prompt
                                    value_index_a = prompt.index(key) + len(key) + 1
                                    # Finds the next quote mark after the key
                                    prompt_after_key = prompt[value_index_a:]
                                    if '"' in prompt[value_index_a:]:
                                        value_index_b = prompt_after_key.index('"')
                                    elif "'" in prompt[value_index_a:]:
                                        value_index_b = prompt_after_key.index("'")
                                    elif not "'" in prompt_after_key and '"' not in prompt_after_key:
                                        # Finds the next space after the key
                                        try:
                                            value_index_b = prompt_after_key.index(" ")
                                        except ValueError:
                                            value_index_b = len(prompt_after_key) + value_index_a
                                    else:
                                        value_index_b = len(prompt_after_key) + value_index_a
                                    # Gets the value from the prompt
                                    value = prompt[value_index_a:value_index_b]

                                    # Adds the key-value pair to the options dictionary
                                    options['kwargs'][key] = value
                                else:
                                    # Handles normal args
                                    options['args'].append(arg)

                        cmd = prompt.split(" ")[0]
                    else:
                        cmd = executing_similar[1]
                        options['args'] = executing_similar[2]
                        # Reset the tuple to prevent infinite loops.
                        # noinspection PyUnusedLocal
                        executing_similar = (False, None, None)

                    if DEBUG == 'True':
                        logging.debug(f'User input: {cmd}')
                        try:
                            # noinspection PyUnboundLocalVariable
                            logging.debug(f"Prompt: {prompt}")
                        except UnboundLocalError:
                            logging.debug("Prompt: None, executing similar command.")
                            # This is for if executing_similar is True
                        logging.debug(f'Options: {options}')

                    if cmd == "":
                        run_success = True
                    elif cmd == "debug":
                        print("DEBUG VALUES:")
                        print(f"DEBUG: {DEBUG}")
                        print(f"Operating System: {platform.platform()}")
                        print(f"Python Version: {platform.python_version()}")
                        print(f"Python Implementation: {platform.python_implementation()}")
                        print(f"Python Compiler: {platform.python_compiler()}")
                        print(f"Timenow: {datetime.datetime.now()}")
                        run_success = True
                    else:
                        # Try to execute a registered command
                        is_alias = self.is_alias(cmd)
                        if cmd in self.registered_commands or is_alias:
                            cmd = self.return_alias_origin(cmd) if is_alias else cmd
                            pass_cmd = self.registered_commands[cmd]['do_pass_cmd']
                            if self.registered_commands[cmd]['uses_args'] is True:
                                if not pass_cmd:
                                    run_success = self.registered_commands[cmd]['func'](options=options)
                                else:
                                    run_success = self.registered_commands[cmd]['func'](options=options, user_cmd=prompt)
                            else:
                                if not pass_cmd:
                                    run_success = self.registered_commands[cmd]['func']()
                                else:
                                    run_success = self.registered_commands[cmd]['func'](user_cmd=prompt)

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
                        # This does not support command kwargs.
                        similar = self.find_similar(cmd, ask_to_execute=True, cmd_args=options['args'])
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
