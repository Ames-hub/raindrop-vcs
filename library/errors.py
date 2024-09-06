class error:
    class project_null(Exception):
        def __init__(self, project_id):
            self.code_number = 1
            self.project_id = project_id
            super().__init__(f"Project {project_id} does not exist.")

    class version_null(Exception):
        def __init__(self, version_id):
            self.code_number = 2
            self.version_id = version_id
            super().__init__(f"Version {version_id} does not exist.")

    class nopassword(Exception):
        def __init__(self, username):
            self.code_number = 3
            super().__init__(f"User {username} does not have a password.")

    class bad_password(Exception):
        def __init__(self):
            self.code_number = 4
            super().__init__("That password is invalid.")

    class bad_token(Exception):
        def __init__(self):
            self.code_number = 5
            super().__init__("That token is invalid.")

    class user_nonexistant(Exception):
        def __init__(self):
            self.code_number = 6
            super().__init__("User does not exist.")

    class user_already_exists(Exception):
        def __init__(self):
            self.code_number = 7
            super().__init__("User already exists.")

    class restricted_account(Exception):
        def __init__(self):
            self.code_number = 8
            super().__init__("This account is restricted from accessing API Functions.")

    class repository_not_found(Exception):
        def __init__(self, repo_name):
            self.code_number = 9
            self.repo_name = repo_name
            super().__init__(f"The repository \"{repo_name}\" does not exist.")

    class password_too_short(Exception):
        def __init__(self):
            self.code_number = 10
            super().__init__("Password is too short.")