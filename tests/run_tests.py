from library.cmd_interface import cli_handler
from library.user_login import user_login
from library.errors import error
from unittest.mock import patch
import pytest
import shutil

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

def test_user_login_with_correct_credentials():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'
        mock_pg_instance.is_user_administrator.return_value = True

        login = user_login(username='testuser', password='correct_password')

        assert login.username == 'testuser'
        assert login.password == 'correct_password'
        assert login.is_admin is True
        mock_pg_instance.check_user_exists.assert_called_once_with('testuser')
        mock_pg_instance.get_password.assert_called_once_with('testuser')

def test_user_login_with_invalid_username():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = False

        with pytest.raises(error.user_nonexistant):
            user_login(username='invaliduser', password='password')

def test_user_login_with_wrong_password():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'

        with pytest.raises(error.bad_password):
            user_login(username='testuser', password='wrong_password')

def test_user_login_with_valid_token():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.validate_token.return_value = True
        mock_pg_instance.get_token_owner.return_value = 'testuser'

        login = user_login(token='valid_token')

        assert login.username == 'testuser'
        mock_pg_instance.validate_token.assert_called_once_with('valid_token')
        mock_pg_instance.get_token_owner.assert_called_once_with('valid_token')

def test_user_login_with_invalid_token():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.validate_token.return_value = False

        with pytest.raises(error.bad_token):
            user_login(token='invalid_token')

def test_generate_token():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'

        login = user_login(username='testuser', password='correct_password')
        token = login.generate_token()

        assert isinstance(token, str)
        assert len(token) > 0
        mock_pg_instance.save_token.assert_called_once_with(belongs_to='testuser', token=token)

def test_is_restricted():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'
        mock_pg_instance.is_restricted.return_value = False

        login = user_login(username='testuser', password='correct_password')
        assert login.is_restricted() is False
        mock_pg_instance.is_restricted.assert_called_once_with('testuser')

def test_set_restricted():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'

        login = user_login(username='testuser', password='correct_password')
        login.set_restricted(True)
        mock_pg_instance.set_restricted.assert_called_once_with('testuser', True)

def test_list_private_repos():
    with patch('library.user_login.PostgreSQL') as mock_pg, patch('os.listdir') as mock_listdir, patch('library.dvcs.rd_config.read_cfg') as mock_read_cfg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'

        mock_listdir.return_value = ['repo1', 'repo2']
        mock_read_cfg.side_effect = [
            {'visibility': 'private', 'description': 'Private Repo'},
            {'visibility': 'public', 'description': 'Public Repo'}
        ]

        login = user_login(username='testuser', password='correct_password')
        repos = login.list_private_repos()

        assert repos == {'repo1': 'Private Repo'}
        mock_listdir.assert_called_once()
        assert mock_read_cfg.call_count == 2

def test_invalid_repository_visibility():
    with patch('library.user_login.PostgreSQL') as mock_pg:
        mock_pg_instance = mock_pg.return_value
        mock_pg_instance.check_user_exists.return_value = True
        mock_pg_instance.get_password.return_value = 'correct_password'

        login = user_login(username='testuser', password='correct_password')

        with pytest.raises(AssertionError):
            login.create_repository('test_repo', 'Test description', 'invalid_visibility')

# Cleanup
shutil.rmtree('data')
shutil.rmtree('logs')