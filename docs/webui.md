<h1 align="center">Raindrop WebUI</h1>

Raindrop's WebUI is the main method of interaction with Raindrop and is the
primary way to manage your Raindrop instance.

On Raindrop's side, it's a very basic system and it's quite hands-off.<br>
If there is a problem, it's likely caused by Nginx, Docker or the OS.

## Prerequisites
- Docker
- Sufficient permissions to run Docker commands.
- At least the minimum system requirements for Nginx.

## How does it work?
That is a question better answered by the team at Nginx or Docker.<br>
But simply put, the WebUI is a website that is hosted on a Nginx server running
in a Docker container.

It creates the nginx docker instance by the use of a terminal command sent<br>
by the use of the 'subprocess' module in Python.

# Setting up the WebUI
### Method 1 (recommended)
Typically, the WebUI is set up automatically when you install Raindrop when it
prompts you to ask if you want to set up the WebUI. If you choose not to set it 
up, you can run in sequence `webui > setup` to set it up. Otherwise, Raindrop's
functionality reduces to just being able to be used via API calls from your own
applications.

### Method 2
In some cases, the installation of the WebUI may fail.<br>
In case this ever happens, or if there is some other reason you need to set up
the WebUI manually, you need to do the following.<br>
1. Navigate to the raindrop main directory in a terminal
2. Copy the full path (from C:/ or / on linux.) of the subdirectory
   `website` in the Raindrop directory and make a note of this.
3. Then in this command
    ```
    docker run -d --name raindrop-webui -p 0.0.0.0:2048:80 -v {website directory}:/usr/share/nginx/html --restart always nginx
    ```
   replace "{website directory}" with the full path of the `website`
   subdirectory we noted in step 2.<br>
   If you wish, you can change the 2048 in `0.0.0.0:2048:80` to any other port
4. Now, the WebUI should be accessible at `http://localhost:2048` or
   `http://<server-ip>:2048` if you are accessing it from another device on the
   same network.

## Breakdown of the command
This command is used in method 1 and 2. Here is a breakdown of the command:<br>
- `docker run` - This command is used to run a new container
- `-d` - This flag is used to run the container in the background
- `--name raindrop-webui` - This flag is used to name the container
- `-p 0.0.0.0:2048:80` - This flag is used to map the container's port 80 to
  the host's port 2048, so the docker container runs the Nginx server on port
  80 but is accessible on port 2048 on the host machine. The 0.0.0.0 is used to
  bind the container to all network interfaces on the host machine.
- `-v {website directory}:/usr/share/nginx/html` - This flag is used to mount
  the website directory in the Raindrop directory to the Nginx server's default
  directory where it serves files from.
- `--restart always` - This flag is used to start or restart the container
  automatically if it crashes or the host machine restarts.