// A basic cache for the fetched data common to Generator and Analyzer

const simpleCache = new Map<string, any>();

/// Returns the cached data or "undefined".
function getFromSimpleCache(cacheKey: string): any {
    return simpleCache.get(cacheKey);
}

function storeInSimpleCache(cacheKey: string, data: any) {
    simpleCache.set(cacheKey, data);
}

export async function fetchJsonFromSimpleCache(cacheKey: string, url: string): Promise<any> {
    let data = getFromSimpleCache(cacheKey);
    if (data === undefined) {
        const jsonData = await fetch(url);
        if (!jsonData.ok) {
            throw new Error(`Error reading data: ${jsonData.status}`);
        }
        data = await jsonData.json();
        storeInSimpleCache(cacheKey, data);
    }
    return data;
}

export async function fetchTextFromSimpleCache(cacheKey: string, url: string): Promise<any> {
    let data = getFromSimpleCache(cacheKey);
    if (data === undefined) {
        const textData = await fetch(url);
        if (!textData.ok) {
            throw new Error(`Error reading data: ${textData.status}`);
        }
        data = await textData.text();
        storeInSimpleCache(cacheKey, data);
    }
    return data;
}

