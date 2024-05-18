document.addEventListener("DOMContentLoaded", function () {
    const { hash } = window.location;
    if (hash) {
        const element = document.querySelector(hash);
        if (element) {
            element.scrollIntoView();
        }
    }
});

document.querySelectorAll('.plot-container').forEach(function(element) {
    element.addEventListener('click', function() {
        const plotName = element.getAttribute('data-plot-name');
        if (plotName) {
            const hashName = plotName.toLowerCase().replace(/\s/g, '-');
            history.pushState(null, null, '#' + hashName);
        }
    });
});