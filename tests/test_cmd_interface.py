from library.cmd_interface import cli_handler
import pytest

# noinspection PyUnusedLocal
def dummy_func(options=None, user_cmd=None):
    return True  # A dummy function for command registration testing.

# Test suite for cli_handler
def test_register_command():
    cli = cli_handler(cli_name="TestCLI")

    # Register a command
    cli.register_command(
        cmd="test",
        func=dummy_func,
        description="A test command",
        aliases=["tst", "example"],
        options={"args": ["arg1", "arg2"]}
    )

    # Check if the command is registered
    assert "test" in cli.cmds_dict
    assert cli.cmds_dict["test"]["msg"] == "A test command"
    assert cli.cmds_dict["test"]["options"]["args"] == ["arg1", "arg2"]

    # Check aliases
    assert cli.is_alias("tst") is True
    assert cli.is_alias("example") is True
    assert cli.is_alias("nonexistent") is False


def test_is_alias():
    cli = cli_handler(cli_name="TestCLI")
    cli.register_command(cmd="hello", func=dummy_func, aliases=["hi", "hey"])

    # Test valid aliases
    assert cli.is_alias("hi") is True
    assert cli.is_alias("hey") is True

    # Test invalid aliases
    assert cli.is_alias("hello") is False
    assert cli.is_alias("unknown") is False


def test_find_similar():
    cli = cli_handler(cli_name="TestCLI")
    cli.register_command(cmd="start", func=dummy_func)
    cli.register_command(cmd="stop", func=dummy_func)

    # Find a similar command
    result = cli.find_similar("stort", [])
    assert result["cmd"] == "start"

    # No similar command
    result = cli.find_similar("unknown", [])
    assert result is None

def test_ask_question(monkeypatch):
    cli = cli_handler(cli_name="TestCLI")

    # Simulate user input
    inputs = iter(["yes", "no", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    # Test valid input
    answer = cli.ask_question("Do you like Python?", options=["yes", "no"])
    assert answer == "yes"

    # Test invalid input followed by valid input
    answer = cli.ask_question("Do you like Python?", options=["yes", "no"])
    assert answer == "no"

    # Test exiting
    with pytest.raises(cli_handler.exited_questioning):
        cli.ask_question("Do you like Python?", exit_phrase="exit")


def test_list_commands(capsys):
    cli = cli_handler(cli_name="TestCLI")
    cli.register_command(cmd="help", func=dummy_func, description="Show help")

    # List commands
    cli.list_commands()
    captured = capsys.readouterr()
    assert "help: Show help" in captured.out

def test_exit():
    cli = cli_handler(cli_name="TestCLI", is_main_cli=True)

    # Test main CLI exit
    with pytest.raises(KeyboardInterrupt):
        cli.exit()

    # Test sub-CLI exit
    cli = cli_handler(cli_name="SubCLI", is_main_cli=False)
    assert cli.exit() is True

def test_plugin_config_loadkeys(tmpdir):
    cli = cli_handler(cli_name="TestCLI")

    # Create a fake plugin config
    plugin_dir = tmpdir.mkdir("plugin")
    plugin_file = plugin_dir.join("plugin.cf")
    plugin_file.write("name=TestPlugin\ndescription=A test plugin\n")

    # Load the config
    result = cli.plugin_config_loadkeys(str(plugin_file))
    assert result["name"] == "TestPlugin"
    assert result["description"] == "A test plugin"