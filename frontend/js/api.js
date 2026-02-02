/**
 * API Client Module
 * Handles all API communication with the backend
 */

const API_BASE = window.location.origin;

/**
 * Check system health
 * @returns {Promise<{status: string, ollama_available: boolean, threads_api_configured: boolean}>}
 */
export async function checkHealth() {
    const response = await fetch(`${API_BASE}/api/health`);
    if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
}

/**
 * Search Threads posts
 * @param {Object} params - Search parameters
 * @param {string} params.keywords - Search keywords
 * @param {string} params.search_type - TOP or RECENT
 * @param {number} params.limit - Number of results
 * @param {string} params.media_type - TEXT, IMAGE, or VIDEO
 * @returns {Promise<Object>} Search results with analysis
 */
export async function searchPosts({ keywords, search_type = 'TOP', limit = 25, media_type = 'TEXT' }) {
    const response = await fetch(`${API_BASE}/api/search`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            keywords,
            search_type,
            limit,
            media_type
        })
    });

    if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
    }

    return response.json();
}

/**
 * Export results as PDF
 * @param {Object} data - Search response data
 * @returns {Promise<Blob>} PDF blob
 */
export async function exportPDF(data) {
    const response = await fetch(`${API_BASE}/api/export-pdf`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        throw new Error('PDF generation failed');
    }

    return response.blob();
}
