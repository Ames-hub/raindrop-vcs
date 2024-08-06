document.addEventListener('DOMContentLoaded', () => {
    // Check if there's a saved state for the sidebar
    let savedState = localStorage.getItem('sidebarState');
    if (savedState) {
        applySidebarState(savedState);
    }
});

let sidebar = document.getElementById('sidebar_left');
let team_logo = document.getElementById('team_logo');
let panel_title = document.getElementById('panel_title');
let status_detector = document.getElementById('status_detector');
let nav_link = document.getElementsByClassName('nav-link');

sidebar.addEventListener('click', (event) => {
    // Check if the clicked element is the sidebar or its immediate children
    if (event.target === sidebar || sidebar.contains(event.target)) {
        // Check if the clicked element is one of the immediate children of the sidebar
        if (event.target !== sidebar) {
            return; // Do nothing if clicked on a child element
        }

        sidebar.style.transition = '0.5s';
        if (sidebar.id === 'shrinked-sidebar') {
            applySidebarState('expanded');
            localStorage.setItem('sidebarState', 'expanded'); // Save state
        } else if (sidebar.id === 'sidebar_left') {
            applySidebarState('shrinked');
            localStorage.setItem('sidebarState', 'shrinked'); // Save state
        }
    }
});

function applySidebarState(state) {
    if (state === 'expanded') {
        sidebar.id = 'sidebar_left';
        team_logo.style.width = '150px';
        document.body.style.marginLeft = '180px';
        team_logo.style.height = '150px';
        panel_title.style.display = 'block';
        status_detector.style.marginTop = '0';
        for (let i = 0; i < nav_link.length; i++) {
            nav_link[i].style.fontSize = '20px';
        }
    } else if (state === 'shrinked') {
        document.body.style.marginLeft = '80px';
        sidebar.id = 'shrinked-sidebar';
        team_logo.style.width = '70px';
        team_logo.style.height = '70px';
        panel_title.style.display = 'none';
        status_detector.style.marginTop = '20px';
        for (let i = 0; i < nav_link.length; i++) {
            nav_link[i].style.fontSize = '0px';
        }
    }
}

function keepAliveCheck () {
    let status_detector = document.getElementById('status_detector');
    let status_text = document.getElementById('status_text');

    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:4096`;

    fetch(api_url)
        .then(response => response.text())
        .then(data => {
            if (data === 'raindrop') {
                status_detector.style.backgroundColor = 'green';
                status_text.innerHTML = 'Online';
            }
            else {
                status_detector.style.backgroundColor = 'red';
                status_text.innerHTML = 'Offline';
            }
        })
        .catch(() => {
            // If it excepts, the server is offline
            status_detector.style.backgroundColor = 'red';
            status_text.innerHTML = 'Offline';
        });
}

keepAliveCheck();
setInterval(keepAliveCheck, 15000);