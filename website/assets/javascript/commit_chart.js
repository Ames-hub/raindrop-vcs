let oldData = null;

// noinspection JSUnusedGlobalSymbols
function update_chart(username) {
    const ctx = document.getElementById('commit_chart').getContext('2d');
    const loadingSpinner = document.getElementById('loading_spinner');
    const commitChart = document.getElementById('commit_chart');

    const currentHost = window.location.hostname;
    const currentProtocol = window.location.protocol;
    const web_url = `${currentProtocol}//${currentHost}:2048`;

    fetch(`${web_url}/api/vcs/commits_chart`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username })
    })
        .then(response => response.json())
        .then(data => {
            let labels = Object.keys(data);
            let values = Object.values(data);

            if (labels.length > 14) {
                labels = labels.slice(0, 14);
                values = values.slice(0, 14);
            }

            const newData = { labels, values };

            if (JSON.stringify(newData) !== JSON.stringify(oldData)) {
                oldData = newData;

                loadingSpinner.style.display = 'none';
                commitChart.style.display = 'block';

                const borderColors = values.map((value, index) => {
                    if (labels[index] === 'n/a') return 'silver';
                    if (index === 0) return 'rgb(20,255,0)';
                    return value <= values[index - 1] ? 'red' : 'rgb(20,255,0)';
                });

                // noinspection JSUnresolvedReference
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Commits Chart',
                            data: values,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                            borderColor: borderColors,
                            borderWidth: 1,
                            segment: {
                                borderColor: ctx => {
                                    // noinspection JSUnresolvedReference
                                    const index = ctx.p0DataIndex;
                                    if (labels[index + 1] === 'n/a') return 'silver';
                                    return values[index + 1] <= values[index] ? 'red' : 'rgb(20,255,0)';
                                }
                            }
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'gray'
                                }
                            },
                            x: {
                                grid: {
                                    color: 'gray'
                                }
                            }
                        },
                        plugins: {
                            zoom: {
                                zoom: {
                                    wheel: {
                                        enabled: true
                                    },
                                    pinch: {
                                        enabled: true
                                    },
                                    mode: 'x',
                                    drag: {
                                        enabled: true,
                                        backgroundColor: 'rgba(0,0,0,0.1)',
                                        borderColor: 'rgba(0,0,0,0.5)',
                                        borderWidth: 1
                                    }
                                }
                            }
                        }
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
