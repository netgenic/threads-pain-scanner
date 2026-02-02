/**
 * Threads Pain Scanner - Main Application Module
 */

import { checkHealth, searchPosts } from './api.js';
import { displayResults, updateStatus, setLoading } from './ui.js';
import { exportResults } from './export.js';

// State
let lastResults = null;

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initHealthCheck();
    initSearchForm();
    initExportButtons();
});

/**
 * Initialize health check
 */
async function initHealthCheck() {
    try {
        const data = await checkHealth();

        if (data.ollama_available) {
            const statusText = data.threads_api_configured
                ? 'API + LLM ✓'
                : 'Demo + LLM ✓';
            updateStatus(true, statusText);
        } else {
            updateStatus(false, 'LLM не найден');
        }
    } catch (error) {
        updateStatus(false, 'Сервер недоступен');
        console.error('Health check failed:', error);
    }
}

/**
 * Initialize search form
 */
function initSearchForm() {
    const searchForm = document.getElementById('search-form');

    searchForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = new FormData(searchForm);
        const keywords = formData.get('keywords').trim();

        if (!keywords) {
            alert('Введите ключевые слова для поиска');
            return;
        }

        setLoading(true);

        try {
            const data = await searchPosts({
                keywords: keywords,
                search_type: formData.get('search_type'),
                limit: parseInt(formData.get('limit')),
                media_type: 'TEXT'
            });

            lastResults = data;
            displayResults(data);

        } catch (error) {
            console.error('Search failed:', error);
            alert('Ошибка при поиске: ' + error.message);
        } finally {
            setLoading(false);
        }
    });
}

/**
 * Initialize export buttons
 */
function initExportButtons() {
    const exportBtns = document.querySelectorAll('[data-export]');

    exportBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const format = btn.dataset.export;
            await exportResults(format, lastResults);
        });
    });
}

// Make exportResults available globally for backwards compatibility
window.exportResults = (format) => exportResults(format, lastResults);
