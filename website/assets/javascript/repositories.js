// TODO: Test this code block
function create_repo(name, description, visibility) {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    fetch(`${api_url}/api/vcs/repository/create`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'repo_name': name,
            'description': description,
            'visibility': visibility
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data['error'] !== undefined) {
                alert(data['error']);
            } else {
                window.location.href = `/view/${localStorage.getItem('username')}/${name}`;
            }
        })
        .catch(() => {
            alert('Error creating repo');
        });
}

// TODO: Test this code block
function delete_repo(name) {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    fetch(`${api_url}/api/vcs/repository/delete`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'repo_name': name
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data['error'] !== undefined) {
                alert(data['error']);
            } else {
                location.reload();
            }
        })
        .catch(() => {
            alert('Error deleting repo');
        });
}

// If page is create.html, then run this code block
if (window.location.pathname === '/repository/create.html') {
    const create_repo_form = document.getElementById('create_repo_form');

    create_repo_form.addEventListener('submit', (e) => {
        e.preventDefault();
        const repo_name = document.getElementById('repo_name').value;

        if (repo_name.includes(' ')) {
            alert('Repository name cannot contain spaces');
            return;
        }
        else if (repo_name.includes('/') || repo_name.includes('\\')) {
            alert('Repository name cannot contain slashes');
            return;
        }
        else if (repo_name === '') {
            alert('Repository name cannot be empty');
            return;
        }

        const repo_description = document.getElementById('repo_desc').value;
        const visibility = document.getElementById('repo_visibility').value;

        create_repo(repo_name, repo_description, visibility);
    });
}

// If page is delete.html, then run this code block instead
if (window.location.pathname === '/repository/delete.html') {
    const delete_repo_form = document.getElementById('delete_repo_form');

    delete_repo_form.addEventListener('submit', (e) => {
        e.preventDefault();
        const repo_name = document.getElementById('repo_name').value;

        delete_repo(repo_name);
    });
}