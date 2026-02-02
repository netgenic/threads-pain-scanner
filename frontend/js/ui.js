/**
 * UI Components Module
 * Handles DOM manipulation and rendering
 */

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Sentiment mapping for display
 */
const SENTIMENT_MAP = {
    'positive': { icon: '😊', text: 'Позитив' },
    'negative': { icon: '😤', text: 'Негатив' },
    'neutral': { icon: '😐', text: 'Нейтрально' },
    'mixed': { icon: '🤔', text: 'Смешанный' },
    'unknown': { icon: '❓', text: 'Неизвестно' }
};

/**
 * Update stats display
 * @param {Object} data - Search response data
 */
export function updateStats(data) {
    document.getElementById('stat-posts').textContent = data.total_posts;

    if (data.analysis) {
        document.getElementById('stat-pains').textContent = data.analysis.pains?.length || 0;
        document.getElementById('stat-ideas').textContent = data.analysis.app_ideas?.length || 0;

        const sentiment = data.analysis.sentiment || 'neutral';
        const sentimentData = SENTIMENT_MAP[sentiment] || SENTIMENT_MAP.neutral;
        document.getElementById('sentiment-icon').textContent = sentimentData.icon;
        document.getElementById('stat-sentiment').textContent = sentimentData.text;
    }
}

/**
 * Render a list of items
 * @param {string} elementId - ID of the list element
 * @param {string[]} items - Items to render
 */
export function renderList(elementId, items) {
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

/**
 * Render keywords cloud
 * @param {string[]} keywords - Keywords to render
 */
export function renderKeywords(keywords) {
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

/**
 * Render posts list
 * @param {Object[]} posts - Posts to render
 */
export function renderPosts(posts) {
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

/**
 * Display full search results
 * @param {Object} data - Search response data
 */
export function displayResults(data) {
    const emptyState = document.getElementById('empty-state');
    const resultsSection = document.getElementById('results-section');

    // Hide empty state, show results
    emptyState.hidden = true;
    resultsSection.hidden = false;

    // Stats
    updateStats(data);

    if (data.analysis) {
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

/**
 * Update status indicator
 * @param {boolean} isOnline - Whether the service is online
 * @param {string} text - Status text
 */
export function updateStatus(isOnline, text) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');

    if (isOnline) {
        statusDot.classList.add('online');
        statusDot.classList.remove('offline');
    } else {
        statusDot.classList.add('offline');
        statusDot.classList.remove('online');
    }

    statusText.textContent = text;
}

/**
 * Set loading state on search button
 * @param {boolean} isLoading - Whether loading
 */
export function setLoading(isLoading) {
    const searchBtn = document.getElementById('search-btn');
    const btnText = searchBtn.querySelector('.btn-text');
    const btnLoader = searchBtn.querySelector('.btn-loader');

    searchBtn.disabled = isLoading;
    btnText.hidden = isLoading;
    btnLoader.hidden = !isLoading;
}
