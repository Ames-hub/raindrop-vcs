const currentHost = window.location.hostname;
const currentProtocol = window.location.protocol;
const api_url = `${currentProtocol}//${currentHost}:2048`;

function AutoSessionCheck() {
    if (window.location.pathname === '/login.html') {
        return; // Do nothing if the window is "login.html"
    }

    fetch(`${api_url}/api/validate/${localStorage.getItem('token')}`)
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Invalid response');
            }
        })
        .then(data => {
            if (data['valid'] === true) {
                // User is still logged in
                console.log("User is still logged in");
            } else {
                // User is no longer logged in
                logoutUser();
            }
        })
        .catch(() => {
            // If it excepts, the server is offline
            logoutUser();
        });
}

function logoutUser() {
    localStorage.removeItem('username');
    localStorage.removeItem('token');
    window.location = `${currentProtocol}//${currentHost}:2048/login.html`;
}

AutoSessionCheck();
setInterval(AutoSessionCheck, 15000);