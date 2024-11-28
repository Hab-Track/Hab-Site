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
            
            if (scrollToCategory) {
                const event = new Event('graphsLoaded');
                document.dispatchEvent(event);
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
