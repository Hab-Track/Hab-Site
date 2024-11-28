document.addEventListener('graphsLoaded', function () {
    const { hash } = window.location;
    if (hash) {
        const element = document.querySelector(hash);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    };


    document.querySelectorAll('.plot-container').forEach(function(element) {
        const plotName = element.getAttribute('data-plot-name');
        if (plotName) {
            const hashName = plotName.toLowerCase().replace(/\s/g, '-');
            element.addEventListener('click', function() {
                history.pushState(null, null, '#' + hashName);
            });
        }
    });
});