self.addEventListener('message', function(e) {
    const { type, data } = e.data;
    
    if (type === 'parse') {
        try {
            const parsed = data.plots.map((plot, index) => ({
                category: data.categories[index],
                data: JSON.parse(plot)
            }));
            
            self.postMessage({
                type: 'parsed',
                data: parsed
            });
        } catch (error) {
            self.postMessage({
                type: 'error',
                error: error.message
            });
        }
    }
});
