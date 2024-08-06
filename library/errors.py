class error:
    class project_null(Exception):
        def __init__(self, project_id):
            self.project_id = project_id
            super().__init__(f"Project {project_id} does not exist.")

    class version_null(Exception):
        def __init__(self, version_id):
            self.version_id = version_id
            super().__init__(f"Version {version_id} does not exist.")
