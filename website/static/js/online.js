let onlineData = [];
let retroInfo = {};

async function loadOnlineStats() {
    try {
        const response = await fetch(onlineStatsUrl);
        const result = await response.json();
        
        if (result.data && result.data.length > 0) {
            onlineData = result.data;
            retroInfo = result.retro_info || {};
            updateStats();
            updateRetrosList();
            createGraph();
        } else {
            showError('No data available');
        }
    } catch (error) {
        console.error('Error loading online stats:', error);
        showError('Failed to load statistics');
    }
}

function updateStats() {
    if (onlineData.length === 0) return;
    
    const latest = onlineData[onlineData.length - 1];
    const retros = latest.retros || {};
    
    const totalOnline = Object.values(retros).reduce((sum, count) => {
        if (typeof count === 'number') {
            return sum + count;
        } else if (typeof count === 'object' && count.avg) {
            return sum + count.avg;
        }
        return sum;
    }, 0);
    
    const retroCount = Object.keys(retros).length;
    
    document.getElementById('total-online').textContent = totalOnline;
    document.getElementById('retro-count').textContent = retroCount;
}

function updateRetrosList() {
    if (onlineData.length === 0) return;
    
    const latest = onlineData[onlineData.length - 1];
    const retros = latest.retros || {};
    
    const retrosList = document.getElementById('retros-list');
    
    const sortedRetros = Object.entries(retros).sort((a, b) => {
        const countA = typeof a[1] === 'number' ? a[1] : a[1].avg || 0;
        const countB = typeof b[1] === 'number' ? b[1] : b[1].avg || 0;
        return countB - countA;
    });
    
    let html = '<h3>Players by Retro</h3><div class="retro-items">';
    
    sortedRetros.forEach(([name, value]) => {
        const count = typeof value === 'number' ? value : value.avg || 0;
        const info = retroInfo[name] || {};
        const website = `https://${name}`;
        const viaRadio = info.via_radio === true;
        const radioIcon = viaRadio ? '<span class="radio-badge" title="Tracked via radio">📻</span>' : '';
        
        html += `
            <a href="${website}" target="_blank" class="retro-item" rel="noopener noreferrer">
                <span class="name">${name} ${radioIcon}</span>
                <span class="count">${count}</span>
            </a>
        `;
    });
    
    html += '</div>';
    retrosList.innerHTML = html;
}

function createGraph() {
    const traces = {};
    
    onlineData.forEach(entry => {
        const timestamp = entry.timestamp;
        const retros = entry.retros || {};
        
        Object.entries(retros).forEach(([retroName, value]) => {
            if (!traces[retroName]) {
                traces[retroName] = {
                    x: [],
                    y: [],
                    name: retroName,
                    mode: 'lines+markers',
                    type: 'scatter',
                    line: { width: 2 },
                    marker: { size: 6 },
                    hovertemplate: '<b style="color: white;">%{fullData.name}</b><br>Players: %{y}<extra></extra>'
                };
            }
            
            traces[retroName].x.push(timestamp);
            
            if (typeof value === 'number') {
                traces[retroName].y.push(value);
            } else if (typeof value === 'object' && value.avg) {
                traces[retroName].y.push(value.avg);
            }
        });
    });
    
    const data = Object.values(traces);
    
    const layout = {
        title: {
            text: 'Online Players History',
            font: { color: 'white', size: 20 }
        },
        xaxis: {
            title: 'Time',
            color: 'white',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        yaxis: {
            title: 'Players Online',
            color: 'white',
            gridcolor: 'rgba(255, 255, 255, 0.1)'
        },
        font: { color: 'white' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        hovermode: 'closest',
        hoverlabel: {
            bgcolor: '#000000',
            font: {
                size: 16,
                family: 'Segoe UI',
                color: 'white'
            },
            bordercolor: 'rgba(255, 255, 255, 0.2)'
        },
        legend: {
            orientation: 'h',
            y: -0.2,
            font: { color: 'white' }
        },
        height: 450,
        margin: { t: 60, b: 80, l: 60, r: 40 }
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
    };
    
    const plotDiv = document.getElementById('online-graph');
    plotDiv.innerHTML = '';
    Plotly.newPlot('online-graph', data, layout, config);
}

function showError(message) {
    const plotDiv = document.getElementById('online-graph');
    plotDiv.innerHTML = `<div class="plot-placeholder">${message}</div>`;
}

document.addEventListener('DOMContentLoaded', function() {
    loadOnlineStats();
    setInterval(loadOnlineStats, 600000); // Refresh every 10 minutes
});
