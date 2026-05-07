class TimeFilter {
    constructor(data, onFilterChange) {
        this.allData = data;
        this.currentFilter = '7d';
        this.onFilterChange = onFilterChange;
    }

    setData(data) {
        this.allData = data;
    }

    getFilteredData() {
        if (this.currentFilter === 'all') {
            return this.allData;
        }

        const now = new Date();
        let cutoffDate;

        switch (this.currentFilter) {
            case '24h':
                cutoffDate = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                break;
            case '7d':
                cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case '30d':
                cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
            default:
                return this.allData;
        }

        return this.allData.filter(entry => {
            const entryDate = new Date(entry.timestamp);
            return entryDate >= cutoffDate;
        });
    }

    setFilter(filter) {
        this.currentFilter = filter;
        if (this.onFilterChange) {
            this.onFilterChange(this.getFilteredData());
        }
    }

    createFilterButtons(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const filters = [
            { id: '24h', label: '24 Hours' },
            { id: '7d', label: '7 Days' },
            { id: '30d', label: '30 Days' },
            { id: 'all', label: 'All Time' }
        ];

        const filterDiv = document.createElement('div');
        filterDiv.className = 'time-filters';

        filters.forEach(filter => {
            const btn = document.createElement('button');
            btn.className = 'time-filter-btn ripple-effect';
            btn.textContent = filter.label;
            btn.dataset.filter = filter.id;
            
            if (filter.id === this.currentFilter) {
                btn.classList.add('active');
            }

            btn.addEventListener('click', () => {
                filterDiv.querySelectorAll('.time-filter-btn').forEach(b => {
                    b.classList.remove('active');
                });
                
                btn.classList.add('active');
                this.setFilter(filter.id);
            });

            filterDiv.appendChild(btn);
        });

        container.insertBefore(filterDiv, container.firstChild);
    }
}
