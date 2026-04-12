(function () {
    const panel = document.getElementById('studioNotificationsPanel');
    if (!panel) {
        return;
    }

    const endpoint = panel.dataset.liveEndpoint;
    const totalCountEl = document.getElementById('studioNotifTotalCount');
    const unreadCountEl = document.getElementById('studioNotifUnreadCount');
    const readCountEl = document.getElementById('studioNotifReadCount');
    const listContainer = document.getElementById('studioNotificationsList');

    if (!endpoint || !totalCountEl || !unreadCountEl || !readCountEl) {
        return;
    }

    function getCsrfToken() {
        const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (tokenInput) {
            return tokenInput.value;
        }

        const cookies = document.cookie ? document.cookie.split(';') : [];
        for (let i = 0; i < cookies.length; i += 1) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return decodeURIComponent(cookie.substring('csrftoken='.length));
            }
        }
        return '';
    }

    function renderEmptyState() {
        if (!listContainer) {
            return;
        }

        listContainer.innerHTML = `
            <div class="empty-state" id="studioNotificationsEmptyState">
                <i class="bi bi-bell-slash" style="font-size: 2.4rem;"></i>
                <h5 class="mt-3 mb-1">No Admin Notifications</h5>
                <p class="mb-0">You are all caught up. Any notices from admin will appear here.</p>
            </div>
        `;
    }

    function renderNotifications(items) {
        if (!listContainer) {
            return;
        }

        if (!items || items.length === 0) {
            renderEmptyState();
            return;
        }

        const csrfToken = getCsrfToken();

        listContainer.innerHTML = items.map((item) => {
            const unreadClass = item.is_read ? '' : ' unread';
            const badge = item.is_read ? '' : '<span class="badge-new">New</span>';
            const action = item.is_read
                ? ''
                : `
                <div class="notification-actions">
                    <form method="post" action="${item.mark_read_url}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <button type="submit" class="btn btn-sm btn-outline-light">Mark Read</button>
                    </form>
                </div>
                `;

            return `
                <article class="notification-item${unreadClass}">
                    <div class="notification-main">
                        <div class="notification-icon">
                            <i class="bi bi-megaphone"></i>
                        </div>
                        <div class="notification-text">
                            <p class="notification-title">${item.message}</p>
                            <div class="notification-meta">
                                <span class="notification-time" title="${item.created_display}">${item.age}</span>
                                ${badge}
                            </div>
                        </div>
                    </div>
                    ${action}
                </article>
            `;
        }).join('');
    }

    async function refreshNotifications() {
        try {
            const response = await fetch(endpoint, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                return;
            }

            const data = await response.json();
            if (!data || !data.success) {
                return;
            }

            totalCountEl.textContent = String(data.total_count || 0);
            unreadCountEl.textContent = String(data.unread_count || 0);
            readCountEl.textContent = String(data.read_count || 0);
            renderNotifications(data.notifications || []);
        } catch (error) {
            // Keep refresh silent to avoid disrupting studio workflow.
        }
    }

    refreshNotifications();
    window.setInterval(refreshNotifications, 30000);
})();
