function vcs_pull(
    repo_name,
    version = 'latest',
    file = '*',
) {
    // Makes a fetch request to the server to pull the latest version of the repository
    fetch('/vcs/repository/pull', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            version: version,
            repo_name: repo_name,
            file: file
        })
    }).then(response => {
        if (response.ok) {
            return response.json()
        } else {
            throw new Error('Failed to pull the repository')
        }
    })
    .then(data => {
        window.location.href = data.url
    })
    .catch(error => {
        console.error(error)
    })
}

// Adds listener for button 'pull_button'
document.getElementById('pull_button').addEventListener('click', () => {
    vcs_pull(
        document.getElementById('repo_name').innerText,
        document.getElementById('ver_sel_label').innerText,
        // Gets all files. Pulls all files in the repository
    )
})
