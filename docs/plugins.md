# Plugin Functionality Documentation

The `cli_handler` class supports plugins, allowing external code to be loaded dynamically to extend the CLI's functionality. Here's how plugins work:

#### Enabling Plugins
- **use_plugins**: When initializing `cli_handler`, you can set `use_plugins=True` to allow plugins to be loaded. If this is enabled, the class will look for plugins in the directory specified by `plugins_dir`.

#### Structure of a Plugin
- A plugin is a Python class that must:
  1. Be initiable with all methods having `self` as the first argument.
  2. Be in a file with the same name as the directory it is in.
  3. Have a method called `main()`—this is the method that gets executed when the plugin is called.
  4. Have a `help()` method to provide help information about the plugin and its use.
  5. Optionally, it may have an `automatic()` method for background tasks that run at intervals if specified in the plugin configuration file.

#### Loading Plugins
- Plugins are loaded from the directory provided in `plugins_dir` using the method `load_plugins_from()`.
  - **load_plugin()** loads a single plugin by file directory and class name.
  
Practically, this means that each plugin should be in its own directory, with the plugin class in a file with the same name as the directory.<br>
All you need to do is place the plugin directory in the `plugins_dir` directory, and the CLI will automatically load it.

#### Plugin Configuration File (`plugin.cf`)
- Each plugin directory should contain a `plugin.cf` configuration file, with keys like:
  - `name`: Name of the plugin (no spaces allowed).
  - `description`: Description of the plugin.
  - `aliases`: Aliases for the plugin command.
  - `do_pass_cmd`: Whether to pass the entire command to the plugin.
  - `func_args`: Arguments the plugin expects.
  - `auto_task_timer`: Time interval for running background tasks.

#### Automatic Background Tasks
- If a plugin specifies an `auto_task_timer`, it must also have an `automatic()` method. The task is run in the background using threading at the specified interval.

### Example Plugin Folder Structure
```
plugins/
│
└───example_plugin/
    │   plugin.cf
    │   example_plugin.py
    |       class in file: example_plugin
    |           must be initiable
    |           methods: *main(self), *help(self), automatic(self)
    └───supporting_files/  # Additional files the plugin may need
```

### Example `plugin.cf` File
```
name=example_plugin
description=An example plugin to demonstrate functionality.
aliases=example,ex
do_pass_cmd=True
auto_task_timer=60
```

The valid keys are determined in the `plugin_config_loadkeys` method in `cli_handler.py`.
```
valid_keys = [
    "name",
    
    "description",
        
    "aliases", # example: myplugin,theplugin,plugin

    "do_pass_cmd", # Whether to pass the full prompt to the CLI to the plugin. Default is False.
    
    "func_args", # This isn't too helpful. Will be removed in the future.
    
    "options", # example: the command may be "example_plugin now", where "now" is an option.
    
    'kw_options', # example: time_to_wait=INT
    
    "expected_options_only", # example: True
    
    "auto_task_timer",  # example: 20 (seconds)
]
```
as of 17/09/2024, this is the list of valid keys.

In this example, the plugin will run background tasks every 60 seconds. The plugin command will also take in the full command input when executed (`do_pass_cmd=True`).
