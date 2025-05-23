function updateGraphs() {
    var showActiveOnly = document.getElementById('show_active_only').checked;
    var newUrl = new URL(window.location.href);
    newUrl.searchParams.set('show_active_only', showActiveOnly ? 'true' : 'false');
    window.history.pushState({}, '', newUrl);
    loadGraphs(false);
}

function loadGraphs(scrollToCategory = true) {
    var showActiveOnly = document.getElementById('show_active_only').checked;
    $.get({
        url: graphsDataUrl,
        data: { show_active_only: showActiveOnly },
        success: function(data) {
            data.categories.forEach(function(category, index) {
                graphData = JSON.parse(data.plots[index]);
                
                var plotDiv = document.getElementById(category);
                if (!plotDiv) {
                    console.error("Plot div not found for category:", category);
                    return;
                }
                
                while (plotDiv.firstChild) {
                    plotDiv.removeChild(plotDiv.firstChild);
                }
                
                plotDiv.classList.remove('plot-placeholder');
                Plotly.newPlot(category, graphData.data, graphData.layout, { responsive: true });
                
                plotDiv.addEventListener('click', function() {
                    history.pushState(null, null, '#' + category);
                });
            });

            if (scrollToCategory) {
                const { hash } = window.location;
                if (hash) {
                    const element = document.querySelector(hash);
                    if (element) {
                        element.scrollIntoView({ behavior: 'smooth' });
                    }
                };
            }
        }
    });
}

$(document).ready(function() {
    var showActiveOnly = new URLSearchParams(window.location.search).get('show_active_only') === 'true';
    $('#show_active_only').prop('checked', showActiveOnly);
    loadGraphs();

    $('#show_active_only').change(function() {
        updateGraphs();
    });
    
    window.addEventListener('popstate', function(event) {
        var showActiveOnly = new URLSearchParams(window.location.search).get('show_active_only') === 'true';
        $('#show_active_only').prop('checked', showActiveOnly);
        loadGraphs();
    });
});