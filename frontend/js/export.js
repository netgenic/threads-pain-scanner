/**
 * Export Module
 * Handles exporting results in various formats
 */

import { exportPDF } from './api.js';

/**
 * Download data as JSON file
 * @param {Object} data - Data to download
 */
export function downloadJson(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `threads-research-${Date.now()}.json`;
    a.click();

    URL.revokeObjectURL(url);
}

/**
 * Download data as CSV file
 * @param {Object} data - Search response data
 */
export function downloadCsv(data) {
    const rows = [
        ['Категория', 'Содержимое']
    ];

    // Add pains
    if (data.analysis?.pains) {
        data.analysis.pains.forEach(pain => {
            rows.push(['Боль', pain]);
        });
    }

    // Add needs
    if (data.analysis?.needs) {
        data.analysis.needs.forEach(need => {
            rows.push(['Потребность', need]);
        });
    }

    // Add ideas
    if (data.analysis?.app_ideas) {
        data.analysis.app_ideas.forEach(idea => {
            rows.push(['Идея', idea]);
        });
    }

    // Add posts
    rows.push(['', '']);
    rows.push(['Посты', '']);
    if (data.posts) {
        data.posts.forEach(post => {
            rows.push(['@' + post.username, post.text.replace(/[\n\r]/g, ' ')]);
        });
    }

    const csvContent = rows.map(row =>
        row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')
    ).join('\n');

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `threads-research-${Date.now()}.csv`;
    a.click();

    URL.revokeObjectURL(url);
}

/**
 * Download data as PDF file
 * @param {Object} data - Search response data
 */
export async function downloadPdf(data) {
    const btn = document.querySelector('button[data-export="pdf"]');
    const originalText = btn.textContent;
    btn.textContent = '⏳';
    btn.disabled = true;

    try {
        const blob = await exportPDF(data);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `threads-report-${Date.now()}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

    } catch (error) {
        console.error('PDF Export error:', error);
        alert('Не удалось скачать PDF: ' + error.message);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

/**
 * Export results in specified format
 * @param {string} format - Export format (json, csv, pdf)
 * @param {Object} data - Data to export
 */
export async function exportResults(format, data) {
    if (!data) {
        alert('Сначала выполните поиск');
        return;
    }

    switch (format) {
        case 'json':
            downloadJson(data);
            break;
        case 'csv':
            downloadCsv(data);
            break;
        case 'pdf':
            await downloadPdf(data);
            break;
    }
}
