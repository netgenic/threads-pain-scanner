/**
 * Threads Pain Scanner - Frontend Application
 */

const API_BASE = window.location.origin;

// State
let lastResults = null;

// DOM Elements
const searchForm = document.getElementById('search-form');
const searchBtn = document.getElementById('search-btn');
const resultsSection = document.getElementById('results-section');
const emptyState = document.getElementById('empty-state');
const statusDot = document.querySelector('.status-dot');
const statusText = document.querySelector('.status-text');

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
});

function setupEventListeners() {
    searchForm.addEventListener('submit', handleSearch);
}

// ============================================
// Health Check
// ============================================

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();

        if (data.ollama_available) {
            statusDot.classList.add('online');
            statusDot.classList.remove('offline');
            statusText.textContent = data.threads_api_configured
                ? 'API + Ollama ✓'
                : 'Demo + Ollama ✓';
        } else {
            statusDot.classList.add('offline');
            statusDot.classList.remove('online');
            statusText.textContent = 'Ollama не найден';
        }
    } catch (error) {
        statusDot.classList.add('offline');
        statusText.textContent = 'Сервер недоступен';
        console.error('Health check failed:', error);
    }
}

// ============================================
// Search Handler
// ============================================

async function handleSearch(event) {
    event.preventDefault();

    const formData = new FormData(searchForm);
    const keywords = formData.get('keywords').trim();

    if (!keywords) {
        alert('Введите ключевые слова для поиска');
        return;
    }

    // UI: Loading state
    setLoading(true);

    try {
        const requestData = {
            keywords: keywords,
            search_type: formData.get('search_type'),
            limit: parseInt(formData.get('limit')),
            media_type: 'TEXT'
        };

        const response = await fetch(`${API_BASE}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        lastResults = data;

        displayResults(data);

    } catch (error) {
        console.error('Search failed:', error);
        alert('Ошибка при поиске: ' + error.message);
    } finally {
        setLoading(false);
    }
}

function setLoading(isLoading) {
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');

    searchBtn.disabled = isLoading;
    btnText.hidden = isLoading;
    btnLoader.hidden = !isLoading;
}

// ============================================
// Display Results
// ============================================

function displayResults(data) {
    // Hide empty state, show results
    emptyState.hidden = true;
    resultsSection.hidden = false;

    // Stats
    document.getElementById('stat-posts').textContent = data.total_posts;

    if (data.analysis) {
        document.getElementById('stat-pains').textContent = data.analysis.pains?.length || 0;
        document.getElementById('stat-ideas').textContent = data.analysis.app_ideas?.length || 0;

        // Sentiment
        const sentiment = data.analysis.sentiment || 'neutral';
        const sentimentMap = {
            'positive': { icon: '😊', text: 'Позитив' },
            'negative': { icon: '😤', text: 'Негатив' },
            'neutral': { icon: '😐', text: 'Нейтрально' },
            'mixed': { icon: '🤔', text: 'Смешанный' },
            'unknown': { icon: '❓', text: 'Неизвестно' }
        };

        const sentimentData = sentimentMap[sentiment] || sentimentMap.neutral;
        document.getElementById('sentiment-icon').textContent = sentimentData.icon;
        document.getElementById('stat-sentiment').textContent = sentimentData.text;

        // Lists
        renderList('pains-list', data.analysis.pains);
        renderList('needs-list', data.analysis.needs);
        renderList('ideas-list', data.analysis.app_ideas);

        // Keywords
        renderKeywords(data.analysis.keywords_found);
    }

    // Posts
    renderPosts(data.posts);
}

function renderList(elementId, items) {
    const list = document.getElementById(elementId);
    list.innerHTML = '';

    if (!items || items.length === 0) {
        list.innerHTML = '<li class="empty-item">Нет данных</li>';
        return;
    }

    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
    });
}

function renderKeywords(keywords) {
    const cloud = document.getElementById('keywords-cloud');
    cloud.innerHTML = '';

    if (!keywords || keywords.length === 0) {
        cloud.innerHTML = '<span class="keyword-tag">Нет ключевых слов</span>';
        return;
    }

    keywords.forEach(keyword => {
        const tag = document.createElement('span');
        tag.className = 'keyword-tag';
        tag.textContent = keyword;
        cloud.appendChild(tag);
    });
}

function renderPosts(posts) {
    const container = document.getElementById('posts-list');
    container.innerHTML = '';

    if (!posts || posts.length === 0) {
        container.innerHTML = '<div class="post-item">Посты не найдены</div>';
        return;
    }

    posts.forEach(post => {
        const div = document.createElement('div');
        div.className = 'post-item';

        const time = new Date(post.timestamp).toLocaleString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });

        div.innerHTML = `
            <div class="post-header">
                <span class="post-username">@${escapeHtml(post.username)}</span>
                <span class="post-time">${time}</span>
            </div>
            <div class="post-text">${escapeHtml(post.text)}</div>
            ${post.permalink ? `<a href="${post.permalink}" target="_blank" class="post-link">Открыть в Threads →</a>` : ''}
        `;

        container.appendChild(div);
    });
}

// ============================================
// Export
// ============================================

async function exportResults(format) {
    if (!lastResults) {
        alert('Сначала выполните поиск');
        return;
    }

    if (format === 'json') {
        downloadJson(lastResults);
    } else if (format === 'csv') {
        downloadCsv(lastResults);
    } else if (format === 'pdf') {
        downloadPdf(lastResults);
    }
}

async function downloadPdf(data) {
    const btn = document.querySelector('button[onclick="exportResults(\'pdf\')"]');
    const originalText = btn.textContent;
    btn.textContent = '⏳';
    btn.disabled = true;

    try {
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

        const blob = await response.blob();
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

function downloadJson(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `threads-research-${Date.now()}.json`;
    a.click();

    URL.revokeObjectURL(url);
}

function downloadCsv(data) {
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

// ============================================
// Utilities
// ============================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
