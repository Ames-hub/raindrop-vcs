### Creating a Plugin for the CLI

To create a plugin for the CLI, follow these steps:

#### 1. Set Up Your Plugin Directory

Normally, this is already setup. However, if it isn't you can do the following:<br>
Create a directory for your plugin inside the `plugins` directory. This directory will contain all the necessary files for your plugin.

Example:
```
plugins/
└── your_plugin/
    ├── plugin
    ├── your_plugin.py
    └── other_files/
```

#### 2. Create the Plugin Config File

Inside your plugin directory, create a file named `plugin` with no extension. This file should contain the name and description of your plugin.

Example content for `plugin` file:
```
your_plugin_name
This is a description of your plugin.
```

#### 3. Create the Main Plugin File

Create a Python file with the same name as your plugin inside your plugin directory. This file should define a class with the same name as the file.

Example structure of an example plugin `red_coloured_cli.py`:
```python
class red_coloured_cli:
    def main(self, *args):  # Remove *args if your plugin does not require arguments.
        # Your plugin's main functionality. This hooks the entire plugin to the CLI.
        red = "\033[91m"
        print(f"{red}Its all red now!")
        if args:
            print(f"Arguments passed: {args}")

    def help(self):
        # All of this code is ran for the help command.
        print("This is a plugin that changes the terminal text to red when ran!")
        print("Usage, do 'red_coloured_cli' in the CLI to see the text change to red.")
```

#### 4. Ensure Required Methods are Present

Your plugin class must have two methods:
- `main`: This method will be executed when the plugin is called.
- `help`: This method will display the help message for the plugin.

#### 5. Register the Plugin

Your plugin will be automatically loaded and registered by the CLI handler if the `use_plugins` parameter is set to `True` when initializing the `cli_handler` class. Ensure that your plugin directory and files are correctly placed inside the `plugins` directory.

Example of initializing the `cli_handler` with plugin support:
```python
from library.cmd_interface import cli_handler
cli = cli_handler(
    cli_name="YourCLI",
    use_plugins=True,
    plugins_dir="plugins"
)
```

#### 6. Test Your Plugin

Start your CLI and test your plugin by typing its name. For example, if your plugin is named `red_coloured_cli`, you can execute it by entering `red_coloured_cli` in the CLI.
The name is determined by the first line in the `plugin` file.

To get help for your plugin, use the `help` command followed by your plugin name:
```
help red_coloured_cli
```

### Example Plugin Directory Structure

```
plugins/
└── sample_plugin/
    ├── plugin
    ├── sample_plugin.py
    └── other_files/
```

Content of `plugin` file:
```
sample_plugin
This is a sample plugin.
```

Content of `sample_plugin.py`:
```python
class SamplePlugin:
    def main(self, *args):
        print("Sample plugin executed with arguments:", args)

    def help(self):
        print("This is the help message for SamplePlugin.")
```