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
            $('#plots').empty();
            Object.keys(data.plots).forEach(function(category) {
                $('#plots').append(
                    '<div id="' + category + '" class="plot-container" data-plot-name="' + category + '">' + data.plots[category] + '</div>'
                );
            });
            
            document.querySelectorAll('.plot-container').forEach(function(element) {
                const plotName = element.getAttribute('data-plot-name');
                if (plotName) {
                    const hashName = plotName.toLowerCase().replace(/\s/g, '-');
                    element.addEventListener('click', function() {
                        history.pushState(null, null, '#' + hashName);
                    });
                }
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
});
