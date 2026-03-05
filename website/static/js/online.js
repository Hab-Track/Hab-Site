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
    
    let allTimePeak = 0;
    let allTimePeakDate = '';
    
    onlineData.forEach(entry => {
        const retros = entry.retros || {};
        const total = Object.values(retros).reduce((sum, count) => {
            const val = typeof count === 'number' ? count : (count.avg || 0);
            return sum + val;
        }, 0);
        
        if (total > allTimePeak) {
            allTimePeak = total;
            allTimePeakDate = entry.timestamp;
        }
    });
    
    document.getElementById('all-time-peak').textContent = allTimePeak;
    document.getElementById('all-time-peak-date').textContent = formatDate(allTimePeakDate);
    
    const now = new Date(latest.timestamp);
    const last24h = onlineData.filter(entry => {
        const entryDate = new Date(entry.timestamp);
        return (now - entryDate) <= 24 * 60 * 60 * 1000;
    });
    
    let peak24h = 0;
    let peak24hTime = '';
    let sum24h = 0;
    
    last24h.forEach(entry => {
        const retros = entry.retros || {};
        const total = Object.values(retros).reduce((sum, count) => {
            const val = typeof count === 'number' ? count : (count.avg || 0);
            return sum + val;
        }, 0);
        
        sum24h += total;
        
        if (total > peak24h) {
            peak24h = total;
            peak24hTime = entry.timestamp;
        }
    });
    
    const avg24h = last24h.length > 0 ? Math.round(sum24h / last24h.length) : 0;
    
    document.getElementById('peak-24h').textContent = peak24h;
    document.getElementById('peak-24h-time').textContent = formatTime(peak24hTime);
    document.getElementById('avg-24h').textContent = avg24h;
    
    updateRetroStatsGrid(last24h);
}

function formatDate(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatTime(timestamp) {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function updateRetroStatsGrid(last24h) {
    if (last24h.length === 0) return;
    
    const latest = onlineData[onlineData.length - 1];
    const currentRetros = latest.retros || {};
    
    const retroStats = {};
    
    last24h.forEach(entry => {
        const retros = entry.retros || {};
        Object.entries(retros).forEach(([name, value]) => {
            if (!retroStats[name]) {
                retroStats[name] = {
                    values: [],
                    peak: 0,
                    peakTime: ''
                };
            }
            
            const count = typeof value === 'number' ? value : value.avg || 0;
            retroStats[name].values.push(count);
            
            if (count > retroStats[name].peak) {
                retroStats[name].peak = count;
                retroStats[name].peakTime = entry.timestamp;
            }
        });
    });
    
    const retroStatsArray = Object.entries(retroStats).map(([name, stats]) => {
        const avg = stats.values.reduce((a, b) => a + b, 0) / stats.values.length;
        const currentValue = currentRetros[name];
        const currentCount = typeof currentValue === 'number' ? currentValue : (currentValue?.avg || 0);
        
        return {
            name,
            current: currentCount,
            avg: Math.round(avg),
            peak: stats.peak,
            peakTime: stats.peakTime
        };
    }).sort((a, b) => b.peak - a.peak);
    
    const grid = document.getElementById('retro-stats-grid');
    let html = '';
    
    retroStatsArray.slice(0, 12).forEach(retro => {
        const info = retroInfo[retro.name] || {};
        const website = `https://${retro.name}`;
        const viaRadio = info.via_radio === true;
        const radioIcon = viaRadio ? '<span class="radio-badge" title="Tracked via radio">📻</span>' : '';
        
        html += `
            <div class="retro-stat-card">
                <div class="retro-stat-header">
                    <a href="${website}" target="_blank" class="retro-stat-name" rel="noopener noreferrer">
                        ${retro.name} ${radioIcon}
                    </a>
                    <span class="retro-current-count">${retro.current} online</span>
                </div>
                <div class="retro-stat-values">
                    <div class="retro-stat-item">
                        <span class="retro-stat-label">24h Peak</span>
                        <span class="retro-stat-value">${retro.peak}</span>
                        <span class="retro-stat-time">${formatTime(retro.peakTime)}</span>
                    </div>
                    <div class="retro-stat-item">
                        <span class="retro-stat-label">24h Avg</span>
                        <span class="retro-stat-value">${retro.avg}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    grid.innerHTML = html;
}

function updateRetrosList() {
    // Function removed - no longer needed
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
                    marker: { size: 5 },
                    hovertemplate: '<b>%{fullData.name}</b><br>Players: %{y}<br>%{x}<extra></extra>'
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
    const isMobile = window.innerWidth <= 768;
    
    const layout = {
        title: {
            text: 'Online Players History',
            font: { 
                color: 'white', 
                size: isMobile ? 16 : 20 
            }
        },
        xaxis: {
            title: isMobile ? '' : 'Time',
            color: 'white',
            gridcolor: 'rgba(255, 255, 255, 0.1)',
            tickfont: { size: isMobile ? 10 : 14 },
            tickangle: isMobile ? -45 : 0
        },
        yaxis: {
            title: isMobile ? '' : 'Players',
            color: 'white',
            gridcolor: 'rgba(255, 255, 255, 0.1)',
            tickfont: { size: isMobile ? 10 : 14 }
        },
        font: { color: 'white' },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        hovermode: 'closest',
        hoverlabel: {
            bgcolor: '#000000',
            font: {
                size: isMobile ? 12 : 16,
                family: 'Segoe UI',
                color: 'white'
            },
            bordercolor: 'rgba(255, 255, 255, 0.2)'
        },
        legend: {
            orientation: 'h',
            y: isMobile ? -0.6 : -0.3,
            font: { 
                color: 'white',
                size: isMobile ? 10 : 12
            },
            bordercolor: 'rgba(255, 255, 255, 0.2)',
            borderwidth: 1
        },
        height: isMobile ? 400 : 450,
        margin: { 
            t: isMobile ? 40 : 60, 
            b: isMobile ? 60 : 80, 
            l: isMobile ? 40 : 60, 
            r: isMobile ? 10 : 40 
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: !isMobile,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'online_stats',
            height: 800,
            width: 1200
        }
    };
    
    const plotDiv = document.getElementById('online-graph');
    plotDiv.innerHTML = '';
    Plotly.newPlot('online-graph', data, layout, config);
    
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            if (onlineData.length > 0) {
                createGraph();
            }
        }, 10);
    });
}

function showError(message) {
    const plotDiv = document.getElementById('online-graph');
    plotDiv.innerHTML = `<div class="plot-placeholder">${message}</div>`;
}

document.addEventListener('DOMContentLoaded', function() {
    loadOnlineStats();
    setInterval(loadOnlineStats, 600000); // Refresh every 10 minutes
});
