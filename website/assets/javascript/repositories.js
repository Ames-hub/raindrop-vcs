const is_repos_html = window.location.pathname.includes("repositories.html");
const make_first_repo_btn = document.getElementById("make_first_repo_btn");
const creationBox = document.getElementById("create_repo_form_container");

function reveal_creation_box() {
    creationBox.style.display = "block";
    // Stops certain buttons from being clicked when the creation box is open
    if (is_repos_html) {
        make_first_repo_btn.disabled = true;
        make_first_repo_btn.style.cursor = "not-allowed";
    }
}

function hide_creation_box() {
    creationBox.style.display = "none";
    if (is_repos_html) {
        make_first_repo_btn.disabled = false;
        make_first_repo_btn.style.cursor = "pointer";
    }
}

// TODO: Test this code block
function create_repo(name, description, is_private) {
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
            'is_private': is_private
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
            alert('Error creating repo');
        });
}

// If the page is "repositories.html", then this code block will be executed
if (is_repos_html) {
    // This code block listens for button press events for "make_first_repo_btn"
    make_first_repo_btn.addEventListener("click", function() {
        // Code to handle button press event for "make_first_repo_btn"
        reveal_creation_box();
    });

    // This code block listens for button press events for "create_repo_btn" (inside the creation box)
    const create_repo_btn = document.getElementById("create_repo_btn");
    create_repo_btn.addEventListener("click", function(event) {
        // Prevent the default form submission
        event.preventDefault();
        
        // Code to handle button press event for "create_repo_btn"
        const repoName = document.getElementById("repo_name_input").value;
        const repoDesc = document.getElementById("repo_desc_input").value;
        const isPrivate = document.getElementById("repo_priv_input").checked;
        create_repo(repoName, repoDesc, isPrivate);
    });
}