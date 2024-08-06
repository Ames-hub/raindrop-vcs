This was written by AI as I could not be f*cked.
## Module: `vcs`

The `vcs` module manages different versions of project files. It provides functionalities to push new versions of files and pull existing versions.

### Imports
- `os`: Provides a way to use operating system-dependent functionality like creating directories, and reading/writing files.
- `error`: Custom error handling module.
- `pylog`: Custom logging module.

### Logging
An instance of the logging class from `pylog` is created to log error messages.

### Class: `vcs`

#### Description
The `vcs` class handles version control for projects. It initializes a directory for the project and provides methods to push new versions of files and pull existing versions.

#### Methods

1. **`__init__(self, project_id)`**
   - **Description**: Initializes the version control system for a project.
   - **Parameters**: 
     - `project_id` (str): The unique identifier for the project.
   - **Logic**:
     - Creates a main directory named "versionControl" if it doesn't exist.
     - Sets the project directory path based on the provided `project_id`.
     - If the project directory does not exist, raises a custom `project_null` error.

2. **`push(self, files_map)`**
   - **Description**: Pushes a new version of the code to the version control system.
   - **Parameters**:
     - `files_map` (list): A list of dictionaries. Each dictionary represents a file with its relative directory and content. The format is:
       ```python
       [
           {
               "filename": {
                   "file_rel_dir": "relative_directory",
                   "file_content": b"file_content_in_bytes"
               }
           },
           ...
       ]
       ```
   - **Logic**:
     - Validates that `files_map` is a non-empty list of dictionaries.
     - Determines the new version ID based on the count of existing versions in the project directory.
     - Creates a new directory for the new version.
     - Iterates over `files_map` to write each file to the appropriate directory.
     - Handles `PermissionError` if there is an issue writing the file and logs the error.

3. **`pull(self, version_id)`**
   - **Description**: Pulls a specific version of the code from the version control system.
   - **Parameters**:
     - `version_id` (int): The version number to pull.
   - **Returns**: 
     - A list of dictionaries in the same format as `files_map` used in the `push` method.
   - **Logic**:
     - Validates that `version_id` is an integer.
     - Constructs the directory path for the specified version.
     - Raises a custom `version_null` error if the version does not exist.
     - Iterates through the files in the version directory and reads their content.
     - Collects file information in the required format and returns it.

### Error Handling
The module raises custom errors from the `error` module to handle specific issues:
- `error.project_null(project_id)`: Raised when the project directory does not exist.
- `error.version_null(version_id)`: Raised when the specified version does not exist.

### Logging
The module uses a custom logging instance to log errors encountered during file operations, specifically `PermissionError` during the `push` method.

---

### Example Usage

```python
from library.versioncontrolsystem import versionControlSystem

# Initialize version control for a project
project_id = "my_project"
vc_system = versionControlSystem(project_id)

# Push a new version
files_map = [
    {
        "file1.txt": {
            "file_rel_dir": "",  # Indicates root directory
            "file_content": open("file1.txt", "rb").read()
        }
    },
    {
        "file2.txt": {
            "file_rel_dir": "docs",
            "file_content": open("file2.txt", "rb").read()
        }
    }
]
vc_system.push(files_map)

# Pull a specific version
version_id = 1
files = vc_system.pull(version_id)
print(files)
```