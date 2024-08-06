<h1 align="center">CLI Handler Class Documentation</h1>

The `cli_handler` class is a command-line interface (CLI) manager designed to handle commands, manage plugins,
and provide user interaction. The class includes functionality to handle both default and custom commands, load and
execute plugins, and manage user input.

*Note: All inputs and command names are case-insensitive (made lower-case).*

# Class Arguments
The class contains a couple of arguments for customization. The arguments are as follows:
- `self` - The class instance. (REQUIRED FOR MOST IF NOT ALL FUNCTIONALITY)
- `cli_name` - The name of the CLI. This will appear in the terminal like<br>
  ```
  Welcome to [cli_name] CLI! Type 'help' for a list of commands.
  CLI_NAME_HERE>
  ```
- greet_func - A function to run when the CLI is started. This function should not take any arguments.<br>
  It should only print a welcome message or something similar. Eg:
  ```python
  def greet():
      is_running = True  # You can check if the server is running here
      print("Welcome to the CLI!")
      print(f"Currently, your server is {'running!' if is_running else 'stopped'}.")
      return True
  ```
- `use_default_cmds` - A boolean value that determines whether to auto-register the default commands<br>
  like 'exit' or 'help' or not. Default is `True`. (not recommended to change to false)
- `use_plugins` - A boolean value that toggles if plugins are allowed to be loaded into the CLI.
   Defaults to False. See `docs/plugins.md` for more information on plugins.
- `plugin_dir` - The directory where the plugins are stored. Defaults to `./plugins/`.
- `is_main_cli` - A boolean value that determines if the CLI is the main CLI or not. Defaults to `True`.<br>
   Only thing it really changes is whether or not it simply sets
   its `self.running` to False or if it raises a KeyboardInterrupt.
  (Only the main CLI raises keyboard interrupt)

# Class Functions
### `exit`
Exits the CLI.
- **Parameters:** None
- **Returns:** None
- **Raises:** 
- `KeyboardInterrupt` if it is the main CLI.
- Sets `self.running` to `False` otherwise.

### `clear_terminal`
Clears the terminal screen.
- **Parameters:** None
- **Returns:** `True`

### `load_plugin`
Loads a single plugin from a directory.
- **Parameters:**
  - `plugin_file_dir` - The directory of the plugin.
  - `class_name` - The name of the class to load.
- **Returns:** `True` if the plugin is loaded successfully, `False` otherwise.
- **Raises:**
  - `ImportError` - If the plugin cannot be imported.
  - `AttributeError` - If the plugin class does not have callable `main` and `help` methods.
  - `ValueError` - If the plugin name contains spaces.
  - `FileNotFoundError` - If the plugin file is not found.

### `load_plugins_from`
Loads all plugins from a specified directory.
- **Parameters:**
  - `plugin_dir` - The directory of the plugins.
- **Returns:** `True`
- **Raises:**
  - `AssertionError` - If the plugin directory does not exist.

### `register_plugin_help_func`
Registers a help function for a plugin.
- **Parameters:**
  - `plugin_name` - The name of the plugin.
  - `help_func` - The help function to register.
- **Returns:** `True`

### `find_similar`
Finds commands and arguments similar to those entered by the user.
- **Parameters:**
  - `cmd` - The command to find similar commands to.
  - `cmd_args` - The arguments of the command.
  - `ask_to_execute` - If `True`, asks the user if they want to execute the similar command.
- **Returns:** 
  - A dictionary with the similar command and arguments if found.
  - `None` if no similar command is found or the user does not want to execute it.

### `ask_question`
Asks the user a question and returns the answer.
- **Parameters:**
  - `question` - The question to ask.
  - `options` - A list of acceptable answers.
  - `exit_phrase` - The phrase to type to exit the question.
  - `confirm_validity` - If `True`, ensures the answer is in the options list.
  - `ask_if_valid` - If `True`, asks the user if the answer is correct.
  - `default` - The default answer if the user enters nothing.
  - `show_default` - If `True`, shows the default answer in the prompt.
  - `filter_func` - A function to filter the answer.
  - `colour` - The color of the prompt.
  - `allow_default` - If `True`, allows the default answer to be returned.
  - `show_options` - If `True`, shows the options list.
  - `exit_notif_msg` - The message indicating how to exit questioning.
  - `clear_terminal` - If `True`, clears the terminal before asking the question.
- **Returns:** The answer to the question.
  - **Raises:** `exited_question` if the user exits the question.

### `exited_question`
Custom exception raised when the user exits a question.

### `list_commands`
Lists all commands that the user can use in the CLI.
- **Parameters:**
  - `return_only` - If `True`, returns the dictionary of commands instead of printing them.
- **Returns:** The dictionary of commands if `return_only` is `True`, `True` otherwise.

### `help_cmd`
Displays help information for all commands or a specific plugin.
- **Parameters:**
  - `args` - The arguments for the help command.
- **Returns:** `True`

### `register_command`
Registers a new command with its corresponding function.
- **Parameters:**
  - `cmd` - The command to register.
  - `func` - The function to execute when the command is called (by cmd being entered into CLI.)
  - `description` - The description of the command.
  - `args` - A list of potential arguments for the command that the user can pass in.
     eg, "Open_Port" command could have "2048" as an argument.
  - `func_args` - The arguments that the function takes invariably. Eg, True passed as the first argument corresponding
     with "Is_from_cli" kwarg.
- **Returns:** `True`

### `main`
Handles the command line interface. This is the main loop of the CLI.
- **Parameters:** None
- **Returns:** None