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

    class password_too_short(Exception):
        def __init__(self):
            self.code_number = 9
            super().__init__("Password is too short.")

    class insufficient_permissions(Exception):
        def __init__(self):
            self.code_number = 10
            super().__init__("You do not have sufficient permission to do that.")

    class json_content_type_only(Exception):
        def __init__(self):
            self.code_number = 11
            super().__init__("The content type is invalid. Please use 'application/json'")

    class GitCommandError(Exception):
        def __init__(self, message):
            self.code_number = 12
            super().__init__(message)

    class InvalidRepositoryError(Exception):
        def __init__(self, message):
            self.code_number = 13
            super().__init__(message)

    class RepositoryNotFound(Exception):
        def __init__(self, message):
            self.code_number = 14
            super().__init__(message)

    class RepositoryAlreadyExists(Exception):
        def __init__(self, message):
            self.code_number = 15
            super().__init__(message)

    class InvalidRepoVisibility(Exception):
        def __init__(self, message):
            self.code_number = 16
            super().__init__(message)

    class RDC_AlreadyExists(Exception):
        def __init__(self, message):
            self.code_number = 17
            super().__init__(message)

    class RDCNotFound(Exception):
        def __init__(self, message):
            self.code_number = 18
            super().__init__(message)

    class RDCWriteError(Exception):
        def __init__(self, message):
            self.code_number = 19
            super().__init__(message)

    class InvalidRDCData(Exception):
        def __init__(self, message):
            self.code_number = 20
            super().__init__(message)

    class InvalidVersionType(Exception):
        def __init__(self, message):
            self.code_number = 21
            super().__init__(message)

    class UserNotFound(Exception):
        def __init__(self, message):
            self.code_number = 22
            super().__init__(message)