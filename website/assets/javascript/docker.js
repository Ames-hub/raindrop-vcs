container_list = document.getElementById('container_list');
function list_containers(containers_dict) {
    container_list.innerHTML = '';

    is_darker = false;
    for (const container in containers_dict) {
        const container_name = containers_dict[container].name;
        const container_status = containers_dict[container].status;
        const container_image = containers_dict[container].image;
        const container_id = containers_dict[container].id;

        const container_div = container_list.appendChild(document.createElement('div'));
        // This statement is equivalent to: "if is_darker is true, then container_div.className = 'docker_container_darker', else container_div.className = 'docker_container'"
        // In other words, its a ternary operator
        container_div.className = is_darker ? 'docker_container_darker' : 'docker_container';
        is_darker = !is_darker;

        // Makes a h1 element with the container name
        const name = container_div.appendChild(document.createElement('h1'));
        name.innerHTML = container_name;

        // Makes a p element with the container status
        const status = container_div.appendChild(document.createElement('p'));
        status.innerHTML = container_status;
        status.className = 'container_status';

        // Makes a p element with the container image
        const image = container_div.appendChild(document.createElement('p'));
        image.innerHTML = container_image;
        image.className = 'container_image';

        // Makes a p element with the container id
        const id = container_div.appendChild(document.createElement('p'));
        id.innerHTML = container_id;
        id.className = 'container_id';
    }
}

// Gets the containers from the API
function get_containers() {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    fetch(`${api_url}/api/docker/list`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}` // Include token in the request headers
        },
    })
        .then(response => response.json())
        .then(data => {
            return data.containers;
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Handles the containers on the page by getting the containers from the API and listing them or displaying a message if there are no containers
function containers_handler() {
    const token = localStorage.getItem('token');
    if (token) {
        const containers = get_containers();  // returns list of dictionaries

        // If there are 0 containers, then add a child element to the container_list div with the text "No containers found"
        if (!containers) {
            container_list.innerHTML = '';
            var message_div = container_list.appendChild(document.createElement('div'));
            message_div.className = 'docker_container';
            var message = message_div.appendChild(document.createElement('h1'));
            message.innerHTML = 'No containers found';
            message.style.textAlign = 'center';
        }
        else {
            list_containers(containers);
        }
    }
}

// Deletes a container with the given container_id
function delete_container(container_id) {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    fetch(`${api_url}/api/docker/delete`, {
        method: 'POST',
        body: JSON.stringify({
            container_id: container_id
        }),
        headers: {
            'Authorization': `Bearer ${token}`, // Include token in the request headers
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

container_list.addEventListener('click', function(event) {
    // If the clicked element is a div with the class "unselected_container", then change the class to "selected_container"
    if (event.target.className === 'unselected_container') {
        event.target.className = 'selected_container';
    }
    // If the clicked element is a div with the class "selected_container", then change the class to "unselected_container"
    else if (event.target.className === 'selected_container') {
        event.target.className = 'unselected_container';
    }
});

// When "delete_selected_btn" is clicked, delete the selected containers (containers with the class "selected_container")
delete_selected_btn = document.getElementById('delete_selected_btn');
delete_selected_btn.addEventListener('click', function() {
    // Confirm that the user wants to delete the selected containers
    selected_count = document.getElementsByClassName('selected_container').length
    if (selected_count === 0) {
        return;
    }

    // If the user clicks "Cancel" on the confirm dialog, then return
    if (!confirm(`You're about to delete ${selected_count} selected containers. Are you ok to continue?`)) {
        return;
    }

    // Delete the selected containers
    const selected_containers = document.getElementsByClassName('selected_container');
    for (const container of selected_containers) {
        const container_id = container.getElementsByClassName('container_id')[0].innerHTML.replace('ID: ', '');
        delete_container(container_id);
    }
    // Update the container list
    containers_handler();
});

containers_handler()
setInterval(containers_handler, 120000); // Update every 2 minutes