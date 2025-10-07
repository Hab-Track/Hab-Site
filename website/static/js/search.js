class NitroReader {
    constructor(arrayBuffer) {
        this.view = new DataView(arrayBuffer);
        this.offset = 0;
    }

    readShort() {
        const value = this.view.getInt16(this.offset);
        this.offset += 2;
        return value;
    }

    readInt() {
        const value = this.view.getInt32(this.offset);
        this.offset += 4;
        return value;
    }

    readString() {
        const length = this.readShort();
        const decoder = new TextDecoder('utf-8');
        const value = decoder.decode(new Uint8Array(this.view.buffer, this.offset, length));
        this.offset += length;
        return value;
    }

    readBytes(length) {
        const bytes = new Uint8Array(this.view.buffer, this.offset, length);
        this.offset += length;
        return bytes;
    }
}

async function processNitroFile(url) {
    try {
        const response = await fetch(url);
        const buffer = await response.arrayBuffer();
        const reader = new NitroReader(buffer);

        const fileCount = reader.readShort();

        for (let i = 0; i < fileCount; i++) {
            const fileName = reader.readString();
            const fileSize = reader.readInt();
            const fileData = reader.readBytes(fileSize);

            if (fileName.endsWith('.png')) {
                try {
                    const decompressed = pako.inflate(fileData);
                    const blob = new Blob([decompressed], { type: 'image/png' });
                    return URL.createObjectURL(blob);
                } catch (e) {
                    console.error('Decompression error:', e);
                }
            }
        }
    } catch (error) {
        console.error('Error processing nitro file:', error);
    }
    return null;
}

document.addEventListener('DOMContentLoaded', function () {
    const dropdownHeader = document.querySelector('.dropdown-header');
    const retrosList = document.querySelector('.retros-list');
    const selectAllCheckbox = document.getElementById('select-all-retros');
    const retroCheckboxes = document.querySelectorAll('input[name="retros"]');
    const retroSearchInput = document.getElementById('retro-search-input');

    retroSearchInput.addEventListener('input', function (e) {
        const searchValue = e.target.value.toLowerCase();
        const retroLabels = document.querySelectorAll('.retros-list label:not(:first-child)');

        retroLabels.forEach(label => {
            const text = label.textContent.toLowerCase();
            label.style.display = text.includes(searchValue) ? 'flex' : 'none';
        });
    });

    dropdownHeader.addEventListener('click', () => {
        retrosList.classList.toggle('show');
        dropdownHeader.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.retros-dropdown')) {
            retrosList.classList.remove('show');
            dropdownHeader.classList.remove('active');
        }
    });

    function updateSelectedCount() {
        const count = [...retroCheckboxes].filter(cb => cb.checked).length;
        document.getElementById('selected-count').textContent = count;
    }

    selectAllCheckbox.addEventListener('change', (e) => {
        retroCheckboxes.forEach(cb => cb.checked = e.target.checked);
        updateSelectedCount();
    });

    retroCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            const allChecked = [...retroCheckboxes].every(checkbox => checkbox.checked);
            selectAllCheckbox.checked = allChecked;
            updateSelectedCount();
        });
    });

    updateSelectedCount();

    document.getElementById('searchForm').addEventListener('submit', async function (e) {
        e.preventDefault();

        const loading = document.getElementById('loading');
        const resultsContainer = document.getElementById('results-container');
        const executionTime = document.getElementById('execution-time');
        const disablePreviews = document.getElementById('disable-previews').checked;

        loading.style.display = 'block';
        resultsContainer.innerHTML = '';
        executionTime.innerHTML = '';

        const formData = new FormData(this);
        const searchQuery = formData.get('search');
        const selectedCategories = formData.getAll('categories');
        const searchIn = formData.getAll('search_in');
        const selectedRetros = formData.getAll('retros');

        if (!searchQuery || selectedRetros.length === 0) {
            loading.style.display = 'none';
            resultsContainer.innerHTML = `<div class="no-results warning">Please enter a search and select at least one retro.</div>`;
            return;
        }

        let mergedResults = {};
        let totalExecutionTime = 0;

        for (const retro of selectedRetros) {
            executionTime.innerHTML = 'Searching retro ' + (selectedRetros.indexOf(retro) + 1) + ' of ' + selectedRetros.length;
            const fd = new FormData();
            fd.append('search', searchQuery);
            for (const cat of selectedCategories) fd.append('categories', cat);
            fd.append('retros', retro);
            for (const sIn of searchIn) fd.append('search_in', sIn);

            try {
                const response = await fetch('/search', { method: 'POST', body: fd });
                const data = await response.json();

                if (data.error || data.warning) {
                    loading.style.display = 'none';
                    resultsContainer.innerHTML = `<div class="no-results error">${data.error || data.warning}</div>`;
                    break;
                }

                totalExecutionTime += data.execution_time || 0;

                if (data.results) {
                    for (const [r, categories] of Object.entries(data.results)) {
                        if (!mergedResults[r]) mergedResults[r] = {};
                        for (const [cat, items] of Object.entries(categories)) {
                            if (!mergedResults[r][cat]) mergedResults[r][cat] = {};
                            Object.assign(mergedResults[r][cat], items);
                        }
                    }
                }
            } catch (error) {
                loading.style.display = 'none';
                resultsContainer.innerHTML = `<div class="no-results error">Network or server error occurred.</div>`;
                console.error(`Error fetching results for retro ${retro}:`, error);
                break;
            }
        }

        loading.style.display = 'none';

        if (Object.keys(mergedResults).length === 0) {
            if (!resultsContainer.querySelector('.error')) {
                resultsContainer.innerHTML = `<div class="no-results">No results found for your search.</div>`;
                executionTime.innerHTML = '';
            }
            return;
        }

        executionTime.innerHTML = `Search completed in ${totalExecutionTime.toFixed(2)} seconds`;

        let html = '';
        for (const [retro, retroData] of Object.entries(mergedResults)) {
            html += `
            <div class="retro-section">
                <h2 class="retro-name">${retro}</h2>
                ${Object.entries(retroData).map(([category, items]) => `
                    <div class="result-category">
                        <h3>${category}</h3>
                        ${Object.entries(items).map(([key, [value, imageUrl, title, description]]) => `
                            <div class="result-item">
                                <div class="result-item-text">
                                    <strong>${value}</strong>
                                    ${title ? `<div class="item-title">${title}</div>` : ''}
                                    ${description ? `<div class="item-description">${description}</div>` : ''}
                                </div>
                                ${!disablePreviews && imageUrl ? `
                                    <a target="_blank" href="${imageUrl}">
                                        <img src="${imageUrl}" 
                                            alt="${value}" 
                                            data-original-url="${imageUrl}"
                                            loading="lazy"
                                            class="result-image">
                                    </a>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                `).join('')}
            </div>
        `;
        }

        resultsContainer.innerHTML = html;

        if (!disablePreviews) {
            const images = resultsContainer.querySelectorAll('.result-image');
            const imageObserver = new IntersectionObserver(async (entries, observer) => {
                for (const entry of entries) {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const originalUrl = img.getAttribute('data-original-url');
                        
                        if (originalUrl && originalUrl.endsWith('.nitro')) {
                            try {
                                const pngUrl = await processNitroFile(originalUrl);
                                if (pngUrl) {
                                    img.src = pngUrl;
                                } else {
                                    img.style.display = 'none';
                                }
                            } catch (error) {
                                console.error('Error processing image:', error);
                                img.style.display = 'none';
                            }
                        }

                        img.onerror = function () {
                            this.style.display = 'none';
                        };
                        
                        observer.unobserve(img);
                    }
                }
            }, {
                rootMargin: '50px 0px',
                threshold: 0.1
            });

            for (const img of images) {
                imageObserver.observe(img);
            }
        }
    });
});