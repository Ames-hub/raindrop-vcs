<h1 align="center">PostgreSQL Setup</h1>

<p align="center">
This guide will help you set up PostgreSQL for Raindrop manually.<br>
Normally, this is not needed, as Raindrop will automatically set up PostgreSQL for you.<br>
However, if you want to set it up manually or there is an unforseen problem with auto-install<br>
this guide will help you do so.
</p>

## Prerequisites
- Docker
- Sufficent permissions to run Docker commands.
- At least the minimum system requirements for PostgreSQL.

## Step 1: Install PostgreSQL
### Method 1: Using Raindrop (Recommended)
1. Start Raindrop's main file.
2. Run the command 'postgre'. This will open up a sub-terminal.
3. Then run the command 'install'. This will install PostgreSQL for you.

And you are done!
### Method 2: Using Docker
This is quite simple. Especially if you do not change the default settings.<br>
1. Firstly, we need to pull Postgres. To do that, simply do this:
    ```bash
    docker pull postgres
    ```
2. Then, we need to install PostgreSQL. You can do this by running the following command:
    ```bash
    docker run --name raindrop-postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 -d postgres
    ```
    Replace `your_password` with your desired password.
3. Now, we need to enter the PostgreSQL container and start an interactive `psql` session. To do this, run the following command:
    ```bash
    docker exec -it raindrop-postgres psql -U postgres
    ```
   You will likely see a prompt for the password. Provide it.
4. Inside the `psql` session, create the database by running:
    ```sql
    CREATE DATABASE raindrop;
    ```
5. Next, create a user by running:
    ```sql
    CREATE USER api-raindrop WITH PASSWORD 'your_password';
    ```
    Replace `your_password` with your desired password.
6. Finally, grant that user untethered access to the database by running:
    ```sql
    GRANT ALL PRIVILEGES ON DATABASE raindrop TO api-raindrop;
    ```
7. Exit the `psql` session by typing:
    ```sql
    \q
    ```

## Step 2: Configure Raindrop
1. Start raindrop's main file.
2. Run the command 'postgre'. This will open up a sub-terminal.
3. Then run the command 'pair'. From there, it will prompt you for connection details.
4. Enter the following details.<br>
    The following details are required:
    - Host: YOUR_HOST (127.0.0.1 if you are running it on the same machine as Raindrop)
    - Port: 5432
    - Database: raindrop
    - User: postgres
    - Password: YOUR_PASSWORD (The password you set in Step 1 part 2)

Once this is done, Raindrop will automatically connect to the database and do the rest for you.<br>
And with that, you are done!

## Usage
You can now use Raindrop as you normally would. PostgreSQL is now set up and ready to go.<br>
But Raindrop has some ways to interact with the database.<br>
This is a list of all the commands you can use:
- `postgre > install` - Installs PostgreSQL for you.
- `postgre > pair` - Setups up DB connection details to the database.
- `postgre > start` - Starts the database if it is not external.
- `postgre > disconnect` - Deletes connection details from the database.
- `postgre > test` - Tests the connection to the database.
- `postgre > exec` - Executes a SQL command on the database. (DANGEROUS)
