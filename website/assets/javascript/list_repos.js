function list_repos(username) {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;

    fetch(`${api_url}/view/${username}/repository/list`, {
    })
        .then(response => response.json())
        .then(data => {
            // Data format: {'repos_list': {repo_name: repo_desc}}
            const repo_list = document.getElementById('repo_list');
            repo_list.innerHTML = '';
            const received_repos = data['repos_list'];
            console.log(received_repos['error']);
            if (received_repos['error'] !== undefined) {
                let no_repos_msg = document.getElementById("no-repos")
                no_repos_msg.style.display = "block";
            }

            received_repos.keys().forEach(repo => {
                const repo_desc = received_repos[repo];
                const repo_item = document.createElement('a');
                repo_item.href = `view/${username}/${repo}`;
                repo_item.className = "repo";
                repo_item.innerText = repo;
                let desc_container = repo_item.appendChild(document.createElement('div'));
                desc_container.className = "desc_container";
                let text = desc_container.appendChild(document.createElement('p'))
                text.innerText = repo_desc;

                repo_list.appendChild(repo_item);
            });
        })
        .catch(() => {
            const repo_list = document.getElementById('repo_list');
            repo_list.innerHTML = '';
            const error_item = document.createElement('a');
            error_item.innerHTML = 'Error fetching repos';
            error_item.style.textAlign = 'center';
            error_item.style.color = 'white';
            repo_list.appendChild(error_item);
        });
}

list_repos('Amelia')
setInterval(list_repos, 120000); // Update every 2 minutes