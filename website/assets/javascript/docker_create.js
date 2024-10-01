function create_container(name, image, internal_port, host_port, host_ip, host_volume, internal_volume, env) {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    fetch(`${api_url}/api/docker/create`, {
        method: 'POST',
        body: JSON.stringify({
            name: name,
            image: image,
            host_port: host_port,
            internal_port: internal_port,
            host_ip: host_ip,
            host_volume: host_volume,
            internal_volume: internal_volume,
            env: env
        }),
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error('Error:', error);
            // Assumes Toast script is loaded
            toast(error);
        });

}

// Listens for create_container_btn click
document.getElementById('create_container_btn').addEventListener('click', function() {
    // Prevents the default form submission
    event.preventDefault();

    // Get the form data
    var form_data = new FormData(document.getElementById('create_container_form'));
    
    var container_name = form_data.get('container_name');
    var container_image = form_data.get('container_image');
    var container_ports = form_data.get('container_ports');
    var host_ip = form_data.get('host_ip');
    var host_volume = form_data.get('host_volume');
    var internal_volume = form_data.get('internal_volume');
    var container_env = form_data.get('container_env');

    console.log(container_name);
    console.log(container_image);
    console.log(container_ports);
    console.log(host_volume);
    console.log(internal_volume);
    console.log(container_env);

    // If the name is > 35 chars, deny it and show a toast 
    if (container_name.length > 40) {
        toast('Container name must be 40 characters or less');
        return;
    }
    else if (container_name.length < 4) {
        toast('Container name must be at least 4 characters');
        return;
    };

    if (container_ports !== "") {
        container_ports = container_ports.split(":");
        if (container_ports.length > 2 || container_ports.length < 2) {
            toast('Invalid port format<br>please use the format below<br><br>ext_port:int_port', 8000);
            return;
        }
        
        var host_port = container_ports[0];
        var internal_port = container_ports[1];
        // If both are not numbers, deny it and show a toast
        if (isNaN(host_port) || isNaN(internal_port)) {
            toast('Ports must be a number.<br>please use the format below<br><br>ext_port:int_port', 8000);
            return;
        }
        // Dont let the container take any of Raindrop's ports
        if (host_port == 2048 || internal_port == 4096) {
            toast('External port cannot be 2048 or 4096 as they are reserved for Raindrop.', 8000);
            return;
        }

        // Sets the ports to integers for the API (as it is not dynamically typed)
        host_port = parseInt(host_port);
        internal_port = parseInt(internal_port);
    }
    else {
        container_ports = null
        var host_port = null;
        var internal_port = null;
    }

    if (host_volume !== "" && internal_volume !== "") {
        // A regex to check if the path is valid on Windows
        var windows_path_regex = /^[a-zA-Z]:[\\/](?:[^\\/:*?"<>|\r\n]+[\\/])*[^\\/:*?"<>|\r\n]*$/;
        // A regex to check if the path is valid on Linux
        var linux_path_regex = /^(\/[^\/\0]+)+\/?$/;
        // If the host path is not valid on any OS, deny it and show a toast
        if (!windows_path_regex.test(host_volume) && !linux_path_regex.test(host_volume)) {
            toast('Host path is invalid on Linux and Windows.<br>please use the format below<br><br>Windows: C:/your/path/here<br>Linux: /your/path/here', 15000);
            return;
        }
        else if (!linux_path_regex.test(internal_volume)) {
            toast('Container internal path is invalid on Linux.<br>please use the format below<br><br>/your/path/here', 8000);
            return;
        }
    }
    else {
        host_volume = null;
        internal_volume = null;
    }

    if (container_env !== "") {
        container_env = container_env.split("=");
        if (container_env.length > 2 || container_env.length < 2) {
            toast('Invalid env format<br>please use the format below<br><br>key=value', 8000);
            return;
        }
    }
    else {
        container_env = null;
    }

    // Create the container
    create_container(container_name, container_image, internal_port, host_port, host_ip, host_volume, internal_volume, container_env);
});