## `cli_handler` Class Documentation

The `cli_handler` class is a command-line interface (CLI) manager designed to handle commands, manage plugins, and provide user interaction. The class includes functionality to handle both default and custom commands, load and execute plugins, and manage user input.

### Imports

- **`from difflib import get_close_matches`**: Used for finding commands that are similar to a mistyped command.
- **`from library.pylog import pylog`**: Custom logging utility.
- **`import importlib.util`**: Used for dynamic module importing.
- **`import platform`**: Provides information about the operating system and Python version.
- **`import dotenv`**: Used to load environment variables from a `.env` file.
- **`import os`**: Provides functionality for interacting with the operating system.

### Initialization

#### `__init__(self, cli_name: str, greet_func=None, use_default_cmds=True, use_plugins=False, plugins_dir='plugins', is_main_cli=False)`

- **Parameters:**
  - `cli_name` (str): Name of the CLI instance.
  - `greet_func` (Optional function): Function to greet the user on each CLI loop.
  - `use_default_cmds` (bool): Whether to use default commands (`help`, `exit`, `cls`, `clear`).
  - `use_plugins` (bool): Whether to enable plugin support.
  - `plugins_dir` (str): Directory where plugins are located.
  - `is_main_cli` (bool): Indicates if this CLI instance is the main CLI or a sub-CLI.

- **Description:**
  Initializes the CLI handler, sets up default commands if specified, and loads plugins if required. Also initializes internal data structures for command registration and plugin management.

### Methods

#### `exit(self)`

- **Description:**
  Exits the CLI. Raises a `KeyboardInterrupt` if this is the main CLI; otherwise, sets the `running` flag to `False` to stop the CLI loop.

#### `clear_terminal(self)`

- **Description:**
  Clears the terminal screen using the appropriate command for the operating system (`cls` for Windows, `clear` for Unix-based systems).

#### `load_plugin(self, plugin_file_dir: str, class_name: str) -> bool`

- **Parameters:**
  - `plugin_file_dir` (str): Path to the plugin file.
  - `class_name` (str): Name of the class to load from the plugin file.

- **Description:**
  Loads a plugin from a specified directory. The plugin class must have `main` and `help` methods. Registers the plugin commands and help function if loading is successful.

#### `load_plugins_from(self, plugin_dir: str) -> bool`

- **Parameters:**
  - `plugin_dir` (str): Directory containing the plugins.

- **Description:**
  Loads all plugins from the specified directory. Each plugin should be in its own subdirectory.

#### `register_plugin_help_func(self, plugin_name: str, help_func) -> bool`

- **Parameters:**
  - `plugin_name` (str): Name of the plugin.
  - `help_func`: Function that provides help for the plugin.

- **Description:**
  Registers a help function for a plugin, allowing the `help` command to provide information about the plugin.

#### `find_similar(self, cmd: str, cmd_args: list, ask_to_execute=False) -> dict | None`

- **Parameters:**
  - `cmd` (str): Command to find similar commands for.
  - `cmd_args` (list): Arguments for the command.
  - `ask_to_execute` (bool): Whether to ask the user if they want to execute the similar command.

- **Description:**
  Finds commands similar to a mistyped command. If `ask_to_execute` is `True`, prompts the user to confirm if they want to execute the similar command.

#### `ask_question(self, question: str, options: list = None, exit_phrase='exit', confirm_validity=True, show_default=True, default=None, filter_func=None, colour='green', do_listing: bool = False, allow_default: bool = True, show_options: bool = True) -> str | list`

- **Parameters:**
  - `question` (str): The question to ask the user.
  - `options` (list, Optional): List of valid options for the response.
  - `exit_phrase` (str): Phrase to exit the question loop.
  - `confirm_validity` (bool): Whether to confirm the validity of the response.
  - `show_default` (bool): Whether to show the default response option.
  - `default` (Optional): Default response if no valid input is given.
  - `filter_func` (Optional function): Function to validate the response.
  - `colour` (str): Colour for the response prompt.
  - `do_listing` (bool): Whether to allow multiple responses.
  - `allow_default` (bool): Whether to allow default value.
  - `show_options` (bool): Whether to show options for the response.

- **Description:**
  Asks a question to the user, with options for validation, default values, and multiple responses if `do_listing` is `True`.

#### `list_commands(self, return_only=False)`

- **Parameters:**
  - `return_only` (bool): Whether to return the dictionary of commands only.

- **Description:**
  Lists all registered commands or returns a dictionary of commands based on the `return_only` flag.

#### `help_cmd(self, args=None)`

- **Parameters:**
  - `args` (Optional list): Arguments for the help command.

- **Description:**
  Provides help information. If arguments are provided, shows help for a specific plugin; otherwise, lists all available commands.

#### `register_command(self, cmd, func, description='', args=[], func_args=None) -> bool`

- **Parameters:**
  - `cmd` (str): Command to register.
  - `func`: Function to execute when the command is called.
  - `description` (str): Description of the command.
  - `args` (list): List of potential arguments for the command.
  - `func_args` (Optional list): Arguments that the function takes.

- **Description:**
  Registers a command with its associated function and description. Also manages command arguments and whether the function requires arguments.

#### `main(self)`

- **Description:**
  Main loop for handling user input. Processes commands, manages execution, and handles errors. Also provides debugging information if enabled.

### Flow of Events

1. **Initialization:**
   - The `cli_handler` is initialized with parameters such as CLI name, greeting function, command settings, and plugin options.
   - Default commands are registered if specified.
   - Plugins are loaded if the `use_plugins` flag is set.

2. **Main Loop:**
   - The `main()` method starts a loop to handle user input.
   - Prompts the user for input and parses the command and arguments.
   - Executes the registered command or handles errors if the command is not found.
   - If an invalid command is entered, tries to find a similar command and prompts the user to confirm execution.

3. **Command Handling:**
   - Commands are executed based on their registration.
   - If a command requires arguments, they are processed and passed to the function.
   - If the command is not found, attempts to find a similar command.

4. **Plugin Management:**
   - Plugins are loaded from specified directories and registered with the CLI.
   - Each plugin must have a `main` method for execution and a `help` method for providing help.

5. **User Interaction:**
   - The CLI handles user questions and options through methods like `ask_question()`.
   - Provides help and command listing features to assist users.

6. **Exit Handling:**
   - The CLI can be exited using the `exit` command or by raising a `KeyboardInterrupt`.
   - If in sub-CLI mode, it returns to the main CLI instead of exiting.

---

This documentation should provide a clear understanding of the `cli_handler` class and its functionality. Let me know if you need any more details or explanations!