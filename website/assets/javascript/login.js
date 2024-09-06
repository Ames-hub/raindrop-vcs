function banner_alert(content) {
    banner = document.getElementById('message_banner');
    message = document.getElementById('message');

    // Set the content of the banner and display it
    message.innerHTML = content;
    banner.style.display = 'block';
    // Hide the banner after 5 seconds
    setTimeout(function() {
        banner.style.display = 'none';
    }, 5000);
}

function attempt_login(form_event) {
    form_event.preventDefault();  // Prevent form from submitting normally
    let username = form_event.target.username.value;
    let password = form_event.target.password.value;

    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048/api/login`;

    fetch(api_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        }),
    })
        .then(response => response.json())
        .then(data => {
            if (data['error'] === null) {
                // Saves the returned token and login username to local storage
                localStorage.setItem('token', data['token']);
                localStorage.setItem('username', username);

                // Redirect to the index page
                window.location.href = `${currentProtocol}//${currentHost}:2048/index.html`;
            } else {
                alert('Invalid username or password');
            }
        })
        .catch(() => {
            alert('Invalid username or password');
        });
}

function attempt_register(form_event) {
    form_event.preventDefault();  // Prevent form from submitting normally
    let username = form_event.target.username.value;
    let password = form_event.target.password.value;

    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048/api/register`;

    fetch(api_url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        }),
    })
        // Check if the user was created successfully or not
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data['success'] === true) {
                alert('User created successfully');
            } else {
                alert(data['error']);
            }
        })
        .catch(() => {
            alert('User already exists');
        });
}

// Check if the server is online or not
function keepAliveCheck() {
    let online_indicator = document.getElementById('online_indicator');

    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const api_url = `${currentProtocol}//${currentHost}:2048/api/status`;

    let login_btn = document.getElementById('login_btn');
    let register_btn = document.getElementById('register_btn');

    fetch(api_url)
        .then(response => response.text())
        .then(data => {
            if (data === 'raindrop') {
                online_indicator.style.backgroundColor = '#28a745';
                login_btn.disabled = false;
                register_btn.disabled = false;
                login_btn.style.cursor = 'pointer';
                register_btn.style.cursor = 'pointer';
                login_btn.style.backgroundColor = '#007bff';
                register_btn.style.backgroundColor = '#28a745';
            } else {
                // Make it red if the server is not online. Also disable clicking "login" or "register" buttons
                online_indicator.style.backgroundColor = '#dc3545';
                login_btn.disabled = true;
                register_btn.disabled = true;
                login_btn.style.cursor = 'not-allowed';
                register_btn.style.cursor = 'not-allowed';
                login_btn.style.backgroundColor = 'gray';
                register_btn.style.backgroundColor = 'gray';
            }
        })
        .catch(() => {
            // If it fails, the server is offline
            online_indicator.style.backgroundColor = 'red';
            login_btn.disabled = true;
            register_btn.disabled = true;
            login_btn.style.cursor = 'not-allowed';
            register_btn.style.cursor = 'not-allowed';
            login_btn.style.backgroundColor = 'gray';
            register_btn.style.backgroundColor = 'gray';
        });
}

keepAliveCheck();
setInterval(keepAliveCheck, 10000); // 10 seconds

// Add event listeners for both forms
document.getElementById('login_form').addEventListener('submit', attempt_login);
document.getElementById('register_form').addEventListener('submit', attempt_register);

// Toggle between login and register form
document.getElementById('toggleForm').addEventListener('change', function(event) {
    const loginForm = document.getElementById('login_form');
    const registerForm = document.getElementById('register_form');

    if (event.target.checked) {
        loginForm.style.display = 'none';
        registerForm.style.display = 'block';
    } else {
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    }
});
