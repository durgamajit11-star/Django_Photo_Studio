(function () {
    document.body.classList.add('studio-dashboard-page');

    const root = document.getElementById('studioDashboardRoot');
    if (!root) {
        return;
    }

    const revenueLabels = JSON.parse(document.getElementById('studioRevenueLabels')?.textContent || '[]');
    const revenueData = JSON.parse(document.getElementById('studioRevenueData')?.textContent || '[]');
    const initialBookingStatus = JSON.parse(document.getElementById('studioBookingStatusData')?.textContent || '[0,0,0]');

    let revenueChart = null;
    let bookingStatusChart = null;

    function axisColors() {
        const light = document.documentElement.getAttribute('data-theme') === 'light';
        return {
            ticks: light ? '#60728b' : '#9eb0cb',
            grid: light ? 'rgba(21,34,56,0.08)' : 'rgba(255,255,255,0.05)'
        };
    }

    function setLastUpdated(text) {
        const node = document.getElementById('lastUpdate');
        if (node) {
            node.textContent = text;
        }
    }

    function applyProgressBars() {
        document.querySelectorAll('.metric-progress-fill').forEach(function (node) {
            const value = Number(node.dataset.width || 0);
            node.style.width = Math.max(0, Math.min(100, value)) + '%';
        });
    }

    function aggregateRevenue(period) {
        if (period === 'month') {
            return { labels: revenueLabels, values: revenueData };
        }

        if (!revenueLabels.length) {
            return { labels: ['No Data'], values: [0] };
        }

        const groupedLabels = [];
        const groupedValues = [];

        if (period === 'quarter') {
            for (let i = 0; i < revenueData.length; i += 3) {
                const chunk = revenueData.slice(i, i + 3);
                const labelStart = revenueLabels[i] || '';
                const labelEnd = revenueLabels[Math.min(i + 2, revenueLabels.length - 1)] || labelStart;
                groupedLabels.push(labelStart === labelEnd ? labelStart : labelStart + ' - ' + labelEnd);
                groupedValues.push(chunk.reduce(function (sum, value) { return sum + Number(value || 0); }, 0));
            }
            return { labels: groupedLabels, values: groupedValues };
        }

        const total = revenueData.reduce(function (sum, value) {
            return sum + Number(value || 0);
        }, 0);
        return { labels: ['All Time'], values: [total] };
    }

    function buildRevenueChart() {
        const canvas = document.getElementById('revenueChart');
        if (!canvas || typeof Chart === 'undefined') {
            return;
        }

        const colors = axisColors();
        const dataSet = aggregateRevenue('month');
        const labels = dataSet.labels.length ? dataSet.labels : ['No Data'];
        const values = dataSet.values.length ? dataSet.values : [0];

        revenueChart = new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue (Rs.)',
                    data: values,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.12)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.35,
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        ticks: { color: colors.ticks },
                        grid: { display: false }
                    },
                    y: {
                        ticks: { color: colors.ticks },
                        grid: { color: colors.grid }
                    }
                }
            }
        });
    }

    function buildBookingStatusChart() {
        const canvas = document.getElementById('bookingStatusChart');
        if (!canvas || typeof Chart === 'undefined') {
            return;
        }

        bookingStatusChart = new Chart(canvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Confirmed', 'Pending', 'Completed'],
                datasets: [{
                    data: initialBookingStatus,
                    backgroundColor: ['#10b981', '#f59e0b', '#3b82f6'],
                    borderWidth: 2,
                    borderColor: '#0f172a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: axisColors().ticks,
                            boxWidth: 12
                        }
                    }
                }
            }
        });
    }

    function wirePeriodSwitch() {
        const switchNode = document.getElementById('revenuePeriodSwitch');
        if (!switchNode || !revenueChart) {
            return;
        }

        switchNode.addEventListener('click', function (event) {
            const button = event.target.closest('button[data-period]');
            if (!button) {
                return;
            }

            const period = button.dataset.period;
            const dataSet = aggregateRevenue(period);

            switchNode.querySelectorAll('button').forEach(function (b) {
                b.classList.toggle('active', b === button);
            });

            revenueChart.data.labels = dataSet.labels.length ? dataSet.labels : ['No Data'];
            revenueChart.data.datasets[0].data = dataSet.values.length ? dataSet.values : [0];
            revenueChart.update();
        });
    }

    function renderTodaySchedule(items) {
        const list = document.getElementById('todayScheduleList');
        if (!list) {
            return;
        }

        if (!items || !items.length) {
            list.innerHTML = '<div class="text-muted small" id="todayScheduleEmpty">No bookings scheduled for today.</div>';
            return;
        }

        list.innerHTML = items.map(function (item) {
            return [
                '<div class="schedule-item">',
                '<div class="schedule-time">' + (item.time || '--') + '</div>',
                '<div class="schedule-details">',
                '<span class="schedule-event">' + (item.event_type || 'Shoot Session') + '</span>',
                '<small class="schedule-client">Client: ' + (item.client || '-') + '</small>',
                '</div>',
                '</div>'
            ].join('');
        }).join('');
    }

    function renderRecentActivity(items) {
        const list = document.getElementById('recentActivityList');
        if (!list) {
            return;
        }

        if (!items || !items.length) {
            list.innerHTML = '<div class="text-muted small" id="recentActivityEmpty">No recent activity available yet.</div>';
            return;
        }

        list.innerHTML = items.map(function (item) {
            return [
                '<div class="notification-item notification-new">',
                '<i class="bi bi-calendar-plus"></i>',
                '<div class="notification-content">',
                '<span class="notification-title">' + (item.event || 'Booking update') + '</span>',
                '<small class="notification-time">' + (item.age || 'Just now') + '</small>',
                '</div>',
                '</div>'
            ].join('');
        }).join('');
    }

    function updateLiveStats(data) {
        const stats = data.stats || {};

        const totalBookings = document.getElementById('statTotalBookings');
        const upcoming = document.getElementById('statUpcomingBookings');
        const revenue = document.getElementById('statTotalRevenue');
        const rating = document.getElementById('statAverageRating');

        if (totalBookings) totalBookings.textContent = String(stats.total_bookings ?? 0);
        if (upcoming) upcoming.textContent = String(stats.confirmed_bookings ?? 0);
        if (revenue) revenue.textContent = 'Rs. ' + String(stats.total_earnings ?? 0);
        if (rating) rating.textContent = String((stats.avg_rating ?? 0).toFixed(1)) + '/5';

        if (Array.isArray(data.booking_status_data) && bookingStatusChart) {
            bookingStatusChart.data.datasets[0].data = data.booking_status_data;
            bookingStatusChart.update();
        }

        renderTodaySchedule(data.today_bookings || []);
        renderRecentActivity(data.recent_activity || []);

        setLastUpdated(data.last_updated || new Date().toLocaleTimeString());
    }

    function pollLive() {
        const endpoint = root.dataset.liveEndpoint;
        if (!endpoint) {
            return;
        }

        fetch(endpoint, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (payload) {
                if (!payload || !payload.success) {
                    return;
                }
                updateLiveStats(payload);
            })
            .catch(function () {
                setLastUpdated('Sync failed');
            });
    }

    buildRevenueChart();
    buildBookingStatusChart();
    wirePeriodSwitch();
    applyProgressBars();
    setLastUpdated(new Date().toLocaleTimeString());

    pollLive();
    window.setInterval(pollLive, 30000);
})();
