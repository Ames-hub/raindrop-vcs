function AutoSessionCheck() {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048`;

    if (window.location.pathname === '/login.html') {
        return; // Do nothing if the window is "login.html"
    }

    fetch(`${api_url}/api/${localStorage.getItem('username')}/validate/${localStorage.getItem('token')}`)
        .then(response => response.text())
        .then(data => {
            if (data === 'raindrop') {
                // User is still logged in
            }
            else {
                // User is no longer logged in
                localStorage.removeItem('username');
                localStorage.removeItem('token');
                window.location = `${currentProtocol}//${currentHost}:2048/login.html`;
            }
        })
        .catch(() => {
            // If it excepts, the server is offline
            status_detector.style.backgroundColor = 'red';
            status_text.innerHTML = 'Offline';
        });
}

AutoSessionCheck();
setInterval(AutoSessionCheck, 15000);