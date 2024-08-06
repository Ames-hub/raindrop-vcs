<h1 align="center">Hosting Raindrop</h1>

Hello! This document will guide you through the process of hosting Raindrop on your own server.<br>
This doc will be assuming you are at least somewhat familar with programming.

## Prerequisites
- Docker Engine
- Python 3.11.9.<br>
  Other versions may work, but they are not officially supported.
- (optional) Port 2048 allowed on your firewall for the WebUI<br>
  This is only needed if you want to access the WebUI from another device.

## Installation
1. Open a terminal
2. Navigate to the directory where you want to install Raindrop<br>
    You can do this with the 'cd' command followed by the path to the directory.
3. Clone the repository with this command:
    ```sh
    git clone https://github.com/Ames-hub/Raindrop-vcs .
    ```
4. Create a virtual environment
    This will take a while on slower devices such as laptops. Be patient.
    ```sh
    python3.11.9 -m venv venv
    ```
    (HANDLING) if Python3.11.9 cannot be located, try just Python3.11<br>
    If it still can't be found, find your Python3.11 installation and replace "Python3.11.9"
    with the path to the Python3.11.9 executable.
5. Activate the virtual environment<br>
   On Linux:
   ```sh
    source venv/bin/activate
    ```
   On Windows:
   ```sh
     venv\Scripts\activate
   ```
6. Install the required Python packages
    ```sh
    pip install -r requirements.txt
    ```
7. Run the server
    ```sh
    python raindrop.py -O
    ```
8. It will then take you through a setup script to ensure all is fine.
    The script is very self-explanatory, so It will not be described here at this date.

## Running the server
On start, a test will be run to see if docker is installed and running. If it is not, the server will not start.<br>
If you are running without docker, Please install it as per docker's instructions.

Other than that, Most processes are either automatic or too simple to bother describing here.<br>
If you have any issues, please open an issue on the GitHub repository.

For any slightly complex or subjects that need explanation, please refer to the other documents in the docs folder.

## Making it global
If you want to make Raindrop globally accessible<br>you will need to port forward port 2048 to your server that runs
both the API and Raindrop.<br>Most routers support this, and if they do not, you can use a service such as<br>Tailscale
(recommended), Ngrok, or Hamachi.

## Manually editing settings
If you need to manually edit settings, you can do so by editing the `settings.json` file in root dir.<br>
NOTE: NEVER SHARE THE SETTINGS.JSON FILE! It contains sensitive information.
In the future, this information will be encrypted using cryptography. But for now, it is plaintext.

## Updating Raindrop (unimplemented)
Raindrop automatically alerts you when an update is available.<br>
To update, in the Raindrop CLI, simply enter `raindrop` then `update`<br><br>
You can set this to automatically run.
However, you can also update using git if that is configured. Just make sure your extra files are not deleted by it.
The point of the update command is to ensure that the update is done without erasing needed files.
