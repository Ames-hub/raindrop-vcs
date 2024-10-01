function add_repo_to_list(repo_name, repo_desc) {
    const repo_item = document.createElement('a');
    repo_item.href = `view/${localStorage.getItem('username')}/${repo_name}`;
    repo_item.className = "repo";
    const repo_title = repo_item.appendChild(document.createElement('h1'));
    repo_title.innerText = repo_name;
    repo_title.className = "repo_title";
    let desc_container = repo_item.appendChild(document.createElement('div'));
    desc_container.className = "desc_container";
    let text = desc_container.appendChild(document.createElement('p'))
    text.innerText = repo_desc;

    repo_list.appendChild(repo_item);
}

// TODO: Fix and bring up to date with current API
function list_containers() {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;
    const token = localStorage.getItem('token');

    function fetchData() {
        fetch(`${api_url}/api/vcs/repositories/list_all`, {
            method: 'GET',
            headers: {
            'Authorization': `Bearer ${token}` // Include token in the request headers
            },
        })
            .then(response => response.json())
            .then(data => {
            // Data format: {'repos_list': {repo_name: repo_desc}}
            const repo_list = document.getElementById('repo_list');
            repo_list.innerHTML = '';

            const private_repos = data['private'];
            const public_repos = data['public'];
            
            if (Object.keys(private_repos).length === 0 && Object.keys(public_repos).length === 0) {
                let no_repos_msg = document.getElementById("no-repos")
                no_repos_msg.style.display = "block";
            }
            else if (data['error'] !== undefined) {
                let error_msg = document.getElementById("error-msg")
                error_msg.style.display = "block";
            }
            
            Object.keys(private_repos).forEach(repo => {
                var repo = private_repos[repo];
                var repo_name = repo['name'];
                var repo_desc = repo['description'];
                add_repo_to_list(repo_name, repo_desc);
                console.log(repo)
            });
            Object.keys(public_repos).forEach(repo => {
                var repo = public_repos[repo];
                var repo_name = repo['name'];
                var repo_desc = repo['description'];
                add_repo_to_list(repo_name, repo_desc);
            });
            })
            .catch(error => {
            console.error('Error fetching repos:', error);
            const repo_list = document.getElementById('repo_list');
            repo_list.innerHTML = '';
            const error_item = document.createElement('a');
            error_item.innerHTML = 'Error fetching repos';
            error_item.style.textAlign = 'center';
            error_item.style.color = 'white';
            repo_list.appendChild(error_item);
            });
    }
    
    fetchData();
}

list_containers()
setInterval(list_containers, 120000); // Update every 2 minutes