class PlotlyLoader {
    constructor() {
        this.loaded = false;
        this.loading = false;
        this.callbacks = [];
        this.PLOTLY_CDN = 'https://cdn.plot.ly/plotly-3.4.0.min.js';
    }

    load() {
        return new Promise((resolve, reject) => {
            if (this.loaded && typeof Plotly !== 'undefined') {
                resolve(Plotly);
                return;
            }

            if (this.loading) {
                this.callbacks.push({ resolve, reject });
                return;
            }

            this.loading = true;

            const script = document.createElement('script');
            script.src = this.PLOTLY_CDN;
            script.async = true;

            script.onload = () => {
                this.loaded = true;
                this.loading = false;
                resolve(Plotly);
                
                this.callbacks.forEach(cb => cb.resolve(Plotly));
                this.callbacks = [];
            };

            script.onerror = (error) => {
                this.loading = false;
                reject(new Error('Failed to load Plotly'));
                
                this.callbacks.forEach(cb => cb.reject(error));
                this.callbacks = [];
            };

            document.head.appendChild(script);
        });
    }

    isLoaded() {
        return this.loaded && typeof Plotly !== 'undefined';
    }
}

const plotlyLoader = new PlotlyLoader();
