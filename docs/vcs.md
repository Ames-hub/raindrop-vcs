# Distributed Version Control System
What is a DVCS? A Distributed Version Control System (DVCS) is a type of version control system
that allows multiple users to work on a project simultaneously. It allows users to create a
local copy of a repository and work on it independently. Users can then push their changes to
the central repository when they are ready to share their work with others. You'd know this
kind of system as git (as in GitHub).

# Raindrop DVCS
Raindrop has its own DVCS system that is much more cut-down and simpler than git.
This does not mean it is less useful, or more useful. It just means it is easier to use
and understand for those with a less technical background. As after all, Raindrop is for the
developer and the writer (although, yes, it is more for the developer. The writer may be better
off with a more dedicated writing tool).

Any development of this tool should be done with that philosophy in mind.

# How it works
Raindrop DVCS works by using two files.<br>
One is cfg.rd and the other is vcs.rd

cfg.rd is the configuration file for the DVCS. It contains the name of the repository,
the owner (by username) of the repository, its SemVer (Major.Minor.Patch), its visibility on
any Raindrop server, its description, and others. It also saves a UUID4 for the repository,
to allow for easy identification without having to iterate through ALL the users and their
repositories to find the one you want. (This is a performance optimization by crossreferencing).

Eg, in a list of thousands of users and repo's, searching by uuid4 can be useful.

| repo_uuid4 | location                                    | 
|------------|---------------------------------------------|
| 1234567    | data/vcs/Raindrop/repositories/Raindrop-vcs | 


vcs.rd is a sqlite3 type file that stores every version of every line by commit version and
by file name.

EG:

| commit_version | file_name | line_number | content          |
|----------------|-----------|-------------|------------------|
| 1              | main.py   | 1           | import os        |
| 1              | main.py   | 2           | import sys       |
| 2              | main.py   | 1           | import os        |
| 2              | main.py   | 2           | import sys       |
| 2              | main.py   | 3           | print("Hello")   |
| 3              | main.py   | 1           | import os        |
| 3              | main.py   | 2           | import sys       |
| 3              | main.py   | 3           | print("Hello")   |
| 3              | main.py   | 4           | print("World")   |

This is a simple example of how the vcs.rd file works. It stores every line of every file
by commit version and by file name. This allows for easy rollback to previous versions of
the code.