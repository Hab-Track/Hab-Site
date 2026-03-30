let onlineData = [];
let retroInfo = {};
let timeFilter;
let resizeTimer;

function stringToColor(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }

    const hue = Math.abs(hash % 360);
    const saturation = 65 + (Math.abs(hash) % 20);
    const lightness = 55 + (Math.abs(hash >> 8) % 15);

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
}

function getRetroColor(retroName) {
    return stringToColor(retroName);
}

function parseTimestamp(timestamp) {
    if (timestamp && /\d{2}:\d{2}[+-Z]/.test(timestamp)) {
        timestamp = timestamp.replace(/(\d{2}:\d{2})([+-Z])/, '$1:00$2');
    }
    return new Date(timestamp);
}

function showSkeletonLoaders() {
    const statsCards = document.querySelectorAll('.stat-card .value');
    statsCards.forEach(card => {
        card.innerHTML = '<div class="skeleton skeleton-text"></div>';
    });

    const graphDiv = document.getElementById('online-graph');
    graphDiv.innerHTML = '<div class="skeleton skeleton-graph"></div>';
}

async function loadOnlineStats(showLoaders = true) {
    if (showLoaders) {
        showSkeletonLoaders();
    }

    try {
        const response = await fetch(onlineStatsUrl);
        const result = await response.json();

        if (result.data && result.data.length > 0) {
            onlineData = result.data;
            retroInfo = result.retro_info || {};
            await initializeData();
        } else {
            showError('No data available');
        }
    } catch (error) {
        console.error('Error loading online stats:', error);
        showError('Failed to load statistics');
    }
}

async function initializeData() {
    updateStats();

    if (!timeFilter) {
        timeFilter = new TimeFilter(onlineData, (filteredData) => {
            createGraph(filteredData);
        });
        timeFilter.createFilterButtons('time-filter-container');
    } else {
        timeFilter.setData(onlineData);
    }

    await plotlyLoader.load();
    createGraph();
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

    const now = parseTimestamp(latest.timestamp);
    const todayMidnight = new Date(now);
    todayMidnight.setHours(0, 0, 0, 0);

    const todayData = onlineData.filter(entry => {
        const entryDate = parseTimestamp(entry.timestamp);
        return entryDate >= todayMidnight;
    });

    let peak24h = 0;
    let peak24hTime = '';
    let sum24h = 0;

    todayData.forEach(entry => {
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

    const avg24h = todayData.length > 0 ? Math.round(sum24h / todayData.length) : 0;

    document.getElementById('peak-24h').textContent = peak24h;
    document.getElementById('peak-24h-time').textContent = formatTime(peak24hTime);
    document.getElementById('avg-24h').textContent = avg24h;

    updateRetroStatsGrid(todayData);
}

function formatDate(timestamp) {
    if (!timestamp) return '-';
    const date = parseTimestamp(timestamp);
    return date.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatTime(timestamp) {
    if (!timestamp) return '-';
    const date = parseTimestamp(timestamp);
    return date.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' });
}

function updateRetroStatsGrid(todayData) {
    if (todayData.length === 0) return;

    const latest = onlineData[onlineData.length - 1];
    const currentRetros = latest.retros || {};

    const allTimePeaks = {};
    onlineData.forEach(entry => {
        const retros = entry.retros || {};
        Object.entries(retros).forEach(([name, value]) => {
            const count = typeof value === 'number' ? value : value.avg || 0;
            if (!allTimePeaks[name] || count > allTimePeaks[name].peak) {
                allTimePeaks[name] = {
                    peak: count,
                    peakTime: entry.timestamp
                };
            }
        });
    });

    const retroStats = {};

    todayData.forEach(entry => {
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
        const allTimePeak = allTimePeaks[name] || { peak: 0, peakTime: '' };

        return {
            name,
            current: currentCount,
            avg: Math.round(avg),
            peak: stats.peak,
            peakTime: stats.peakTime,
            allTimePeak: allTimePeak.peak,
            allTimePeakTime: allTimePeak.peakTime
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
                        <span class="retro-stat-label">AT Peak</span>
                        <span class="retro-stat-value">${retro.allTimePeak}</span>
                        <span class="retro-stat-time">${formatDate(retro.allTimePeakTime)}</span>
                    </div>
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

function createGraph(dataToPlot = null) {
    const traces = new Map();
    const filteredData = dataToPlot || timeFilter?.getFilteredData() || onlineData;

    for (const entry of filteredData) {
        const timestamp = parseTimestamp(entry.timestamp);
        const retros = entry.retros || {};

        for (const [retroName, value] of Object.entries(retros)) {
            if (!traces.has(retroName)) {
                const color = getRetroColor(retroName);
                traces.set(retroName, {
                    x: [],
                    y: [],
                    name: retroName,
                    mode: 'lines+markers',
                    type: 'scatter',
                    line: { width: 2, color },
                    marker: { size: 5, color },
                    hovertemplate: '<b>%{fullData.name}</b><br>Players: %{y}<br>%{x}<extra></extra>'
                });
            }

            const trace = traces.get(retroName);
            trace.x.push(timestamp);
            trace.y.push(typeof value === 'number' ? value : (value.avg || 0));
        }
    }

    const plotData = Array.from(traces.values());
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
            color: 'white',
            gridcolor: 'rgba(255, 255, 255, 0.1)',
            tickfont: { size: isMobile ? 10 : 14 },
            tickangle: isMobile ? -45 : 0,
            type: 'date'
        },
        yaxis: {
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
        annotations: [
            {
                x: 0.5,
                y: isMobile ? -0.6 : -0.3,
                xref: 'paper',
                yref: 'paper',
                yanchor: 'bottom',
                text: 'Double click on a retro to isolate it',
                showarrow: false,
                font: { color: 'white', size: isMobile ? 10 : 12 }
            }
        ],
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
    
    if (plotDiv.classList.contains('graph-loaded')) {
        Plotly.react('online-graph', plotData, layout, config);
    } else {
        plotDiv.innerHTML = '';
        Plotly.newPlot('online-graph', plotData, layout, config);
        plotDiv.classList.add('graph-loaded');
    }
}

function setupResizeHandler() {
    window.removeEventListener('resize', handleResize);
    window.addEventListener('resize', handleResize);
}

function handleResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        if (onlineData.length > 0 && timeFilter) {
            createGraph(timeFilter.getFilteredData());
        }
    }, 100);
}

function showError(message) {
    const plotDiv = document.getElementById('online-graph');
    plotDiv.innerHTML = `<div class="plot-placeholder">${message}</div>`;
}

document.addEventListener('DOMContentLoaded', function () {
    setupResizeHandler();
    loadOnlineStats(true);
    setInterval(() => loadOnlineStats(false), 300000);
});
