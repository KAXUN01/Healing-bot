// Function to format bytes to human-readable format
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Function to update the dashboard
function updateDashboard() {
    fetch('/metrics')
        .then(response => response.text())
        .then(data => {
            const metrics = {};
            data.split('\n').forEach(line => {
                if (!line.startsWith('#') && line.trim()) {
                    const [key, value] = line.split(' ');
                    metrics[key] = parseFloat(value);
                }
            });

            // Update System Overview
            updateProgressBar('cpuLoad', metrics['cpu_load_simulation'] || 0);
            updateProgressBar('memoryUsage', metrics['memory_usage_percent'] || 0);
            updateProgressBar('systemCpu', metrics['system_cpu_percent'] || 0);

            // Update Process Information
            document.getElementById('virtualMemory').textContent = formatBytes(metrics['process_virtual_memory_bytes'] || 0);
            document.getElementById('residentMemory').textContent = formatBytes(metrics['process_resident_memory_bytes'] || 0);
            document.getElementById('openFds').textContent = metrics['process_open_fds'] || 0;
            document.getElementById('cpuTime').textContent = (metrics['process_cpu_seconds_total'] || 0).toFixed(2) + ' seconds';

            // Update charts
            updateGCObjectsChart(metrics);
            updateGCCollectionsChart(metrics);

            // Update Python Info
            updatePythonInfo(metrics);
        });
}

function updateProgressBar(id, value) {
    const progressBar = document.getElementById(id);
    const textElement = document.getElementById(id + 'Text');
    const percentage = Math.min(Math.max(value, 0), 100);
    
    progressBar.style.width = `${percentage}%`;
    textElement.textContent = `${percentage.toFixed(1)}%`;

    if (percentage < 60) {
        progressBar.className = 'progress-bar bg-success';
    } else if (percentage < 80) {
        progressBar.className = 'progress-bar bg-warning';
    } else {
        progressBar.className = 'progress-bar bg-danger';
    }
}

let gcObjectsChart = null;
function updateGCObjectsChart(metrics) {
    const ctx = document.getElementById('gcObjectsChart');
    const data = {
        labels: ['Generation 0', 'Generation 1', 'Generation 2'],
        datasets: [
            {
                label: 'Objects Collected',
                data: [
                    metrics['python_gc_objects_collected_total{generation="0"}'] || 0,
                    metrics['python_gc_objects_collected_total{generation="1"}'] || 0,
                    metrics['python_gc_objects_collected_total{generation="2"}'] || 0
                ],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            },
            {
                label: 'Objects Uncollectable',
                data: [
                    metrics['python_gc_objects_uncollectable_total{generation="0"}'] || 0,
                    metrics['python_gc_objects_uncollectable_total{generation="1"}'] || 0,
                    metrics['python_gc_objects_uncollectable_total{generation="2"}'] || 0
                ],
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }
        ]
    };

    if (!gcObjectsChart) {
        gcObjectsChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } else {
        gcObjectsChart.data = data;
        gcObjectsChart.update();
    }
}

let gcCollectionsChart = null;
function updateGCCollectionsChart(metrics) {
    const ctx = document.getElementById('gcCollectionsChart');
    const data = {
        labels: ['Generation 0', 'Generation 1', 'Generation 2'],
        datasets: [{
            label: 'Collections',
            data: [
                metrics['python_gc_collections_total{generation="0"}'] || 0,
                metrics['python_gc_collections_total{generation="1"}'] || 0,
                metrics['python_gc_collections_total{generation="2"}'] || 0
            ],
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    };

    if (!gcCollectionsChart) {
        gcCollectionsChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } else {
        gcCollectionsChart.data = data;
        gcCollectionsChart.update();
    }
}

function updatePythonInfo(metrics) {
    const pythonInfo = document.getElementById('pythonInfo');
    const version = `${metrics['python_info{implementation="CPython",major="3",minor="9",patchlevel="23",version="3.9.23"}'] ? '3.9.23' : 'Unknown'}`;
    pythonInfo.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <strong>Implementation:</strong> CPython
            </div>
            <div class="col-md-6">
                <strong>Version:</strong> ${version}
            </div>
        </div>
    `;
}

// Update the dashboard every 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    updateDashboard();
    setInterval(updateDashboard, 5000);
});