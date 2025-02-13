# Updated Plugin Development Guide for CLI Handler

This guide provides comprehensive instructions for creating and integrating plugins with the CLI handler defined in `cmd_interface.py`. It combines the existing documentation with new insights and clarifications.

---

## **Plugin Overview**
Plugins extend the CLI's functionality by allowing external code to be dynamically loaded. They are directories containing:
1. A Python file with a class implementing `main()` and `help()`.
2. A configuration file (`plugin.cf`) with metadata and settings.

---

## **Enabling Plugins**
To enable plugins, initialize the `cli_handler` with `use_plugins=True` and specify the `plugins_dir` (default is `plugins/`):
```python
cli = cli_handler(
    cli_name="DemoCLI",
    use_plugins=True,
    plugins_dir="plugins"  # default
)
cli.main()
```

---

## **Plugin Structure**
Each plugin must follow this structure:
```
plugins/
  └── my_plugin/
      ├── my_plugin.py
      └── plugin.cf
```

### **1. Python File (`my_plugin.py`)**
The Python file must contain a class with:
- **`main(self, options: dict)`**: Executes the plugin's logic.
- **`help(self)`**: Displays usage instructions.
- **`automatic(self)`** (optional): Runs periodically if `auto_task_timer` is set in `plugin.cf`.

#### Example: `my_plugin.py`
```python
class my_plugin:
    def main(self, options: dict):
        """Handles the command 'my_plugin [args] [kwargs]'"""
        args = options.get("args", [])
        kwargs = options.get("kwargs", {})
        
        # Example: my_plugin Alice repeat=3
        if args:
            user = args[0]
            print(f"Hello, {user}!")
        else:
            print("Hello, world!")
        
        repeat = kwargs.get("repeat", 1)
        for _ in range(repeat):
            print("This is a repeated message.")

    def help(self):
        """Displays help for this plugin"""
        print("Usage: my_plugin [user] [repeat=int]")
        print("Example: my_plugin Alice repeat=3")

    def automatic(self):
        """Runs every 10 seconds (from plugin.cf)"""
        print("Automated task running...")
```

---

### **2. Configuration File (`plugin.cf`)**
The `plugin.cf` file defines the plugin's metadata and behavior. Example:
```ini
name = my_plugin
description = A demo plugin that greets users.
aliases = greet,hello
do_pass_cmd = False
options = user,time
kw_options = repeat=int
auto_task_timer = 10
expected_options_only = True
```

#### **Key Descriptions**
| Key                  | Description                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `name`               | Command name to invoke the plugin (no spaces).                             |
| `description`        | Short description shown in `help`.                                         |
| `aliases`            | Comma-separated alternate names for the command.                           |
| `do_pass_cmd`        | If `True`, passes the full user command string to `main()`.                |
| `options`            | List of positional arguments the plugin accepts (e.g., `user,time`).       |
| `kw_options`         | Keyword arguments and types (e.g., `repeat=int`).                          |
| `auto_task_timer`    | Interval (seconds) to run `automatic()` method. Use `-1` to disable.       |
| `expected_options_only` | If `True`, rejects unrecognized arguments.                              |

---

## **Plugin Loading**
Plugins are automatically loaded from the `plugins_dir` directory. The CLI handler uses:
- **`load_plugins_from(plugins_root_dir)`**: Loads all plugins from the specified directory.
- **`load_plugin(plugin_file_dir, class_name)`**: Loads a single plugin by file path and class name.

---

## **Using the Plugin**
1. **Run the main command**:
   ```
   DemoCLI> my_plugin Alice
   Hello, Alice!
   ```
2. **Use keyword arguments**:
   ```
   DemoCLI> my_plugin repeat=3
   Hello, world!
   This is a repeated message.
   This is a repeated message.
   This is a repeated message.
   ```
3. **View help**:
   ```
   DemoCLI> help my_plugin
   Usage: my_plugin [user] [repeat=int]
   Example: my_plugin Alice repeat=3
   ```

---

## **Advanced Features**
### **Automated Tasks**
- If `auto_task_timer` is set in `plugin.cf`, the `automatic()` method runs periodically in the background.
- Example: A plugin with `auto_task_timer=60` will run `automatic()` every 60 seconds.

### **Thread Safety**
- Use `threading.Lock` in `automatic()` if modifying shared resources.

### **Sub-CLIs**
- Plugins can create nested CLIs by instantiating `cli_handler` internally.

---

## **Troubleshooting**
- **Plugin not loading?** Check:
  - Correct directory structure.
  - Valid `plugin.cf` syntax.
  - No spaces in `name`.
  - `main()` and `help()` methods exist.
- **Logs**: Check `logs/[date].log` for errors.

---

## **Valid Keys in `plugin.cf`**
The `plugin_config_loadkeys` method in `cli_handler.py` defines valid keys:
```python
valid_keys = [
    "name",
    "description",
    "aliases",  # example: myplugin,theplugin,plugin
    "do_pass_cmd",  # Whether to pass the full prompt to the CLI to the plugin. Default is False.
    "func_args",  # This isn't too helpful. Will be removed in the future.
    "options",  # example: the command may be "example_plugin now", where "now" is an option.
    'kw_options',  # example: time_to_wait=INT
    "expected_options_only",  # example: True
    "auto_task_timer",  # example: 20 (seconds)
]
```

---

## **Example Plugin Folder Structure**
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

---

## **Conclusion**
Plugins are a powerful way to extend the CLI's functionality. By following this guide, you can create, configure, and integrate plugins seamlessly. For further assistance, refer to the `cmd_interface.py` source code or the logs for debugging.