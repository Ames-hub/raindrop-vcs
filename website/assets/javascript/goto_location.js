function get_web_url () {
    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    return `${currentProtocol}//${currentHost}:2048`;
}

function goto_profile_href () {
    // TODO: Ensure user cannot reach any page with the sidebar if not logged in
    window.location = `${get_web_url()}/view/${localStorage.getItem('username')}`;
}

function goto_index_href () {
    window.location = `${get_web_url()}/`;
}

function goto_repositories_href () {
    window.location = `${get_web_url()}/repositories.html`;
}