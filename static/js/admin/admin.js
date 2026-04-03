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

    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
});


