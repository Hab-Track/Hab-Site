class CacheManager {
    constructor() {
        this.CACHE_PREFIX = 'habtrack_';
    }

    set(key, data, customDuration = null) {
        try {
            const cacheKey = this.CACHE_PREFIX + key;
            const duration = customDuration || 60 * 60 * 1000;
            
            const cacheData = {
                data: data,
                timestamp: Date.now(),
                expires: Date.now() + duration
            };
            
            localStorage.setItem(cacheKey, JSON.stringify(cacheData));
            return true;
        } catch (e) {
            console.warn('Cache set failed:', e);
            return false;
        }
    }

    get(key) {
        try {
            const cacheKey = this.CACHE_PREFIX + key;
            const cached = localStorage.getItem(cacheKey);
            
            if (!cached) return null;
            
            const cacheData = JSON.parse(cached);
            
            if (Date.now() > cacheData.expires) {
                this.remove(key);
                return null;
            }
            
            return cacheData.data;
        } catch (e) {
            console.warn('Cache get failed:', e);
            return null;
        }
    }

    remove(key) {
        try {
            const cacheKey = this.CACHE_PREFIX + key;
            localStorage.removeItem(cacheKey);
        } catch (e) {
            console.warn('Cache remove failed:', e);
        }
    }
}

const cache = new CacheManager();
