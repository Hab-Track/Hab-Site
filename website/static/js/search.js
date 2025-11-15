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

    const abortButton = document.getElementById('abort-search');
    abortButton.style.display = 'none';
    let isAborting = false;
    let currentController = null;

    abortButton.addEventListener('click', () => {
        if (currentController) {
            isAborting = true;
            currentController.abort();
            loading.style.display = 'none';
            abortButton.style.display = 'none';
            executionTime.innerHTML = 'Search aborted';
        }
    });

    document.getElementById('searchForm').addEventListener('submit', async function (e) {
        e.preventDefault();

        const loading = document.getElementById('loading');
        const resultsContainer = document.getElementById('results-container');
        const executionTime = document.getElementById('execution-time');
        const disablePreviews = document.getElementById('disable-previews').checked;

        isAborting = false;

        loading.style.display = 'block';
        abortButton.style.display = 'block';
        resultsContainer.innerHTML = '';
        executionTime.innerHTML = '';

        const formData = new FormData(this);
        const searchQuery = formData.get('search');
        const selectedCategories = formData.getAll('categories');
        const searchIn = formData.getAll('search_in');
        const selectedRetros = formData.getAll('retros');

        if (!searchQuery || selectedRetros.length === 0) {
            loading.style.display = 'none';
            abortButton.style.display = 'none';
            resultsContainer.innerHTML = `<div class="no-results warning">Please enter a search and select at least one retro.</div>`;
            return;
        }

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

        executionTime.innerHTML = 'Searching...';

        try {
            currentController = new AbortController();
            const response = await fetch('/search', {
                method: 'POST',
                body: formData,
                signal: currentController.signal
            });
            const data = await response.json();

            loading.style.display = 'none';
            abortButton.style.display = 'none';

            if (data.error || data.warning) {
                resultsContainer.innerHTML = `<div class="no-results error">${data.error || data.warning}</div>`;
                executionTime.innerHTML = '';
                return;
            }

            if (!data.results || Object.keys(data.results).length === 0) {
                resultsContainer.innerHTML = `<div class="no-results">No results found for your search.</div>`;
                executionTime.innerHTML = '';
                return;
            }

            for (const [retro, categories] of Object.entries(data.results)) {
                const retroSection = document.createElement('div');
                retroSection.className = 'retro-section';
                retroSection.setAttribute('data-retro', retro);
                retroSection.innerHTML = `<h2 class="retro-name">${retro}</h2>`;
                resultsContainer.appendChild(retroSection);

                for (const [cat, items] of Object.entries(categories)) {
                    const categorySection = document.createElement('div');
                    categorySection.className = 'result-category';
                    categorySection.setAttribute('data-category', cat);
                    categorySection.innerHTML = `<h3>${cat}</h3>`;
                    retroSection.appendChild(categorySection);

                    const itemsContainer = document.createElement('div');
                    itemsContainer.className = 'items-container';

                    Object.entries(items).forEach(([key, [value, imageUrl, title, description]]) => {
                        const itemHtml = `
                            <div class="result-item" data-key="${key}">
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
                        `;
                        itemsContainer.insertAdjacentHTML('beforeend', itemHtml);
                    });

                    const existingItems = categorySection.querySelector('.items-container');
                            if (existingItems) {
                                existingItems.remove();
                            }
                            itemsContainer.className = 'items-container';
                    categorySection.appendChild(itemsContainer);

                    if (!disablePreviews) {
                        const images = itemsContainer.querySelectorAll('.result-image');
                        for (const img of images) {
                            imageObserver.observe(img);
                        }
                    }
                }
            }

            executionTime.innerHTML = `Search completed in ${data.execution_time.toFixed(2)} seconds`;

        } catch (error) {
            loading.style.display = 'none';
            abortButton.style.display = 'none';
            
            if (error.name === 'AbortError') {
                resultsContainer.innerHTML = `<div class="no-results warning">Search aborted by user.</div>`;
                executionTime.innerHTML = '';
            } else {
                resultsContainer.innerHTML = `<div class="no-results error">Network or server error occurred.</div>`;
                executionTime.innerHTML = '';
                console.error('Error fetching results:', error);
            }
        }
    });
});
