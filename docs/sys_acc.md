# The system account
This write-up will detail how to manually create the system account.<br>
All steps to this are necessary to ensure the system account is created properly.

# Note before we start
If this is too complicated to follow, please contact the developer for assistance
in setting up the system account.<br> I am always happy to help so long as you are respectful.

## Storage
The system account is stored in the database.
Its existence is denoted by the existence of the account "Raindrop" in the database,
and by the existence of the folder "Raindrop" in the data/users/raindrop and data/repos/raindrop
folder

## Creation
```sql
INSERT INTO accounts (username, password)
VALUES ('Raindrop', 'YOUR_PASSWORD_HERE');
```
Replace YOUR_PASSWORD_HERE with the password you want to use for the system account.
Then run the command in the PostgreSQL database.

## Folder creation
Then, find the data folder in the root of this project.
(If you don't have one, create one)

Inside the data folder, create a folder called "users" and inside that folder,
create a folder called "raindrop".

Then, in the data folder where we started,
create a folder called "repos" and inside that folder, create a folder called "raindrop".

## Setting as administrator
```sql
INSERT INTO user_permissions (username, administrator)
VALUES ('Raindrop', true);
```
Run this command in the PostgreSQL database to set the system account as an administrator.

This should be all that is needed to create an account.