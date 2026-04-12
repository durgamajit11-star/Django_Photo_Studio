(function () {
    const panel = document.getElementById('dashboardNotificationsPanel');
    const countBadge = document.getElementById('dashboardUnreadCount');
    const listContainer = document.getElementById('dashboardRecentNotifications');

    if (!panel || !countBadge) {
        return;
    }

    const endpoint = panel.dataset.liveEndpoint;
    if (!endpoint) {
        return;
    }

    function renderNotifications(items) {
        if (!listContainer) {
            return;
        }

        if (!items || items.length === 0) {
            listContainer.innerHTML = '<div class="alert alert-secondary mb-0">No notifications right now.</div>';
            return;
        }

        listContainer.innerHTML = items.map((item) => {
            const statusBadge = item.is_read ? '' : '<span class="badge bg-warning text-dark">New</span>';
            const borderClass = item.is_read ? '' : ' border-info';

            return `
                <div class="mini-item d-flex justify-content-between align-items-center gap-2${borderClass}">
                    <div class="min-w-0">
                        <div class="fw-semibold text-truncate">${item.message}</div>
                        <div class="small text-secondary">${item.age}</div>
                    </div>
                    ${statusBadge}
                </div>
            `;
        }).join('');
    }

    async function refreshDashboardNotifications() {
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
            if (!data || data.success !== true) {
                return;
            }

            countBadge.textContent = String(data.unread_count || 0);
            renderNotifications(data.recent_notifications || []);
        } catch (error) {
            // Ignore silent refresh errors to avoid interrupting dashboard usage.
        }
    }

    refreshDashboardNotifications();
    window.setInterval(refreshDashboardNotifications, 30000);
})();
