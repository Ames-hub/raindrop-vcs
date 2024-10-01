function create_container(name, image, ports, volumes, env) {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    fetch(`${api_url}/api/docker/create`, {
        method: 'POST',
        body: JSON.stringify({
            name: name,
            image: image,
            ports: ports,
            volumes: volumes,
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
    var host_volume = form_data.get('host_volume');
    var internal_volume = form_data.get('internal_volume');
    var container_env = form_data.get('container_env');

    // If the name is > 35 chars, deny it and show a toast 
    if (container_name.length > 40) {
        toast('Container name must be 40 characters or less');
        return;
    };
    if (container_name.length < 4) {
        toast('Container name must be at least 4 characters');
        return;
    };

    if (container_ports !== null) {
        container_ports = container_ports.split(":");
        if (container_ports.length > 2 || container_ports.length < 2) {
            toast('Invalid port format<br>please use the format below<br><br>ext_port:int_port', 8000);
            return;
        }
        // If both are not numbers, deny it and show a toast
        if (isNaN(container_ports[0]) || isNaN(container_ports[1])) {
            toast('Ports must be a number.<br>please use the format below<br><br>ext_port:int_port', 8000);
            return;
        }
        // Dont let the container take any of Raindrop's ports
        if (container_ports[0] == 2048 || container_ports[0] == 4096) {
            toast('External port cannot be 2048 or 4096 as they are reserved for Raindrop.', 8000);
            return;
        }
    };

    if (host_volume !== null && internal_volume !== null) {
        // A regex to check if the path is valid on Windows
        var windows_path_regex = /^[a-zA-Z]:[\\/](?:[^\\/:*?"<>|\r\n]+[\\/])*[^\\/:*?"<>|\r\n]*$/;
        // A regex to check if the path is valid on Linux
        var linux_path_regex = /^(\/[^\/\0]+)+\/?$/;
        // If the host path is not valid on any OS, deny it and show a toast
        if (!windows_path_regex.test(host_volume) && !linux_path_regex.test(host_volume)) {
            toast('Host path is invalid on Linux and Windows.<br>please use the format below<br><br>Windows: C:/host/path:/container/path<br>Linux: /host/path:/container/path', 15000);
            return;
        }
        else if (!linux_path_regex.test(internal_volume)) {
            toast('Container internal path is invalid on Linux.<br>please use the format below<br><br>host_path:container_path', 8000);
            return;
        }
    }
    else if (host_volume !== null && internal_volume === null) {
        toast('Please provide an internal path for the volume.', 8000);
        return;
    }
    else if (host_volume === null && internal_volume !== null) {
        toast('Please provide a host path for the volume.', 8000);
        return;
    }

    if (container_env !== null) {
        container_env = container_env.split("=");
        if (container_env.length > 2 || container_env.length < 2) {
            toast('Invalid env format<br>please use the format below<br><br>key=value', 8000);
            return;
        }
    };

    // Create the container
    create_container(container_name, container_image, container_ports, container_volumes, container_env);
});