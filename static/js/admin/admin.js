document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.admin-sidebar');
    const toggleBtn = document.querySelector('#sidebarToggle');
    const toggleIcon = document.querySelector('#sidebarToggleIcon');
    const toggleLabel = document.querySelector('#sidebarToggleLabel');
    const mobileToggle = document.querySelector('#mobileSidebarToggle');

    function syncSidebarToggleState() {
        if (!sidebar || !toggleBtn) return;
        const collapsed = sidebar.classList.contains('collapsed');
        toggleBtn.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        toggleBtn.setAttribute('title', collapsed ? 'Expand Sidebar' : 'Collapse Sidebar');
        if (toggleLabel) {
            toggleLabel.textContent = collapsed ? 'Expand Sidebar' : 'Collapse Sidebar';
        }
        if (toggleIcon) {
            toggleIcon.className = collapsed ? 'bi bi-layout-sidebar-inset-reverse' : 'bi bi-layout-sidebar-inset';
        }
    }

    if (sidebar && localStorage.getItem('adminSidebar') === 'collapsed') {
        sidebar.classList.add('collapsed');
    }
    syncSidebarToggleState();

    if (sidebar && toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');
            syncSidebarToggleState();
            localStorage.setItem(
                'adminSidebar',
                sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded'
            );
        });
    }

    if (sidebar && mobileToggle) {
        mobileToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });

        document.addEventListener('click', function (event) {
            const clickedInsideSidebar = sidebar.contains(event.target);
            const clickedToggle = mobileToggle.contains(event.target);
            if (!clickedInsideSidebar && !clickedToggle) {
                sidebar.classList.remove('show');
            }
        });
    }

    const revenueChartCanvas = document.getElementById('revenueChart');
    const labelsElement = document.getElementById('revenue-labels');
    const dataElement = document.getElementById('revenue-data');

    if (revenueChartCanvas && labelsElement && dataElement && typeof Chart !== 'undefined') {
        const revenueLabels = JSON.parse(labelsElement.textContent);
        const revenueData = JSON.parse(dataElement.textContent);
        function getChartThemeColors() {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            return {
                gridColor: isDark ? 'rgba(148, 163, 184, 0.2)' : 'rgba(18, 34, 56, 0.10)',
                tickColor: isDark ? '#dbe5f3' : '#31445f',
                barColor: isDark ? 'rgba(34, 193, 180, 0.78)' : 'rgba(15, 157, 143, 0.78)',
            };
        }

        const initialColors = getChartThemeColors();

        const revenueChart = new Chart(revenueChartCanvas, {
            type: 'bar',
            data: {
                labels: revenueLabels,
                datasets: [
                    {
                        label: 'Revenue',
                        data: revenueData,
                        backgroundColor: initialColors.barColor,
                        borderRadius: 8,
                        borderSkipped: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
                scales: {
                    x: {
                        ticks: {
                            color: initialColors.tickColor,
                        },
                        grid: {
                            color: initialColors.gridColor,
                        },
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: initialColors.tickColor,
                        },
                        grid: {
                            color: initialColors.gridColor,
                        },
                    },
                },
            },
        });

        document.addEventListener('studiosync:theme-changed', function () {
            const next = getChartThemeColors();
            revenueChart.data.datasets[0].backgroundColor = next.barColor;
            revenueChart.options.scales.x.ticks.color = next.tickColor;
            revenueChart.options.scales.y.ticks.color = next.tickColor;
            revenueChart.options.scales.x.grid.color = next.gridColor;
            revenueChart.options.scales.y.grid.color = next.gridColor;
            revenueChart.update('none');
        });

        window.addEventListener('resize', function () {
            revenueChart.resize();
        });
    }

    const policyTrendCanvas = document.getElementById('policyTrendChart');
    const policyTrendLabelsEl = document.getElementById('policy-trend-labels');
    const policyTrendBlockedEl = document.getElementById('policy-trend-blocked');
    const policyTrendFaqRateEl = document.getElementById('policy-trend-faq-rate');

    if (
        policyTrendCanvas &&
        policyTrendLabelsEl &&
        policyTrendBlockedEl &&
        policyTrendFaqRateEl &&
        typeof Chart !== 'undefined'
    ) {
        const labels = JSON.parse(policyTrendLabelsEl.textContent);
        const blockedSeries = JSON.parse(policyTrendBlockedEl.textContent);
        const faqRateSeries = JSON.parse(policyTrendFaqRateEl.textContent);

        function getPolicyTrendThemeColors() {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            return {
                gridColor: isDark ? 'rgba(148, 163, 184, 0.2)' : 'rgba(18, 34, 56, 0.10)',
                tickColor: isDark ? '#dbe5f3' : '#31445f',
                blockedColor: isDark ? 'rgba(251, 191, 36, 0.75)' : 'rgba(217, 119, 6, 0.75)',
                faqRateColor: isDark ? 'rgba(52, 211, 153, 0.95)' : 'rgba(5, 150, 105, 0.95)',
            };
        }

        const colors = getPolicyTrendThemeColors();
        const policyTrendChart = new Chart(policyTrendCanvas, {
            data: {
                labels,
                datasets: [
                    {
                        type: 'bar',
                        label: 'Blocked Intents',
                        data: blockedSeries,
                        yAxisID: 'y',
                        backgroundColor: colors.blockedColor,
                        borderRadius: 7,
                        borderSkipped: false,
                    },
                    {
                        type: 'line',
                        label: 'FAQ Hit Rate %',
                        data: faqRateSeries,
                        yAxisID: 'y1',
                        borderColor: colors.faqRateColor,
                        backgroundColor: colors.faqRateColor,
                        pointRadius: 3,
                        pointHoverRadius: 4,
                        tension: 0.35,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        labels: {
                            color: colors.tickColor,
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: {
                            color: colors.tickColor,
                        },
                        grid: {
                            color: colors.gridColor,
                        },
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                            color: colors.tickColor,
                        },
                        grid: {
                            color: colors.gridColor,
                        },
                        title: {
                            display: true,
                            text: 'Blocked Intents',
                            color: colors.tickColor,
                        },
                    },
                    y1: {
                        beginAtZero: true,
                        max: 100,
                        position: 'right',
                        ticks: {
                            color: colors.tickColor,
                            callback: function (value) {
                                return `${value}%`;
                            },
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                        title: {
                            display: true,
                            text: 'FAQ Hit Rate %',
                            color: colors.tickColor,
                        },
                    },
                },
            },
        });

        document.addEventListener('studiosync:theme-changed', function () {
            const next = getPolicyTrendThemeColors();
            policyTrendChart.data.datasets[0].backgroundColor = next.blockedColor;
            policyTrendChart.data.datasets[1].borderColor = next.faqRateColor;
            policyTrendChart.data.datasets[1].backgroundColor = next.faqRateColor;
            policyTrendChart.options.plugins.legend.labels.color = next.tickColor;
            policyTrendChart.options.scales.x.ticks.color = next.tickColor;
            policyTrendChart.options.scales.y.ticks.color = next.tickColor;
            policyTrendChart.options.scales.y1.ticks.color = next.tickColor;
            policyTrendChart.options.scales.y.title.color = next.tickColor;
            policyTrendChart.options.scales.y1.title.color = next.tickColor;
            policyTrendChart.options.scales.x.grid.color = next.gridColor;
            policyTrendChart.options.scales.y.grid.color = next.gridColor;
            policyTrendChart.update('none');
        });
    }

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    const selectAllStudios = document.getElementById('selectAllStudios');
    const studioChecks = Array.from(document.querySelectorAll('.studio-select'));
    const selectedStudioCount = document.getElementById('selectedStudioCount');

    function syncSelectedStudiosCount() {
        if (!selectedStudioCount) return;
        const selected = studioChecks.filter(function (item) { return item.checked; }).length;
        selectedStudioCount.textContent = `${selected} selected`;
    }

    if (selectAllStudios && studioChecks.length) {
        selectAllStudios.addEventListener('change', function () {
            studioChecks.forEach(function (checkbox) {
                checkbox.checked = selectAllStudios.checked;
            });
            syncSelectedStudiosCount();
        });

        studioChecks.forEach(function (checkbox) {
            checkbox.addEventListener('change', function () {
                const allSelected = studioChecks.every(function (item) { return item.checked; });
                selectAllStudios.checked = allSelected;
                syncSelectedStudiosCount();
            });
        });

        syncSelectedStudiosCount();
    }
});


