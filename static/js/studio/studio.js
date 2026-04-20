// ===============================
// STUDIO DASHBOARD JS
// ===============================

document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.studio-sidebar');
    const desktopToggle = document.querySelector('#studioSidebarToggleBtn');
    const toggleIcon = document.querySelector('#studioSidebarToggleIcon');
    const mobileToggle = document.querySelector('#mobileStudioSidebarToggle');

    function syncSidebarToggleState() {
        if (!sidebar || !desktopToggle) return;
        const collapsed = sidebar.classList.contains('collapsed');
        desktopToggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        desktopToggle.setAttribute('title', collapsed ? 'Expand Sidebar' : 'Collapse Sidebar');
        if (toggleIcon) {
            toggleIcon.className = collapsed ? 'bi bi-layout-sidebar-inset-reverse' : 'bi bi-layout-sidebar-inset';
        }
    }

    function applySidebarStateForViewport() {
        if (!sidebar) return;
        if (window.innerWidth <= 992) {
            sidebar.classList.remove('collapsed');
        } else {
            sidebar.classList.remove('show');
            if (localStorage.getItem('studioSidebar') === 'collapsed') {
                sidebar.classList.add('collapsed');
            } else {
                sidebar.classList.remove('collapsed');
            }
        }
        syncSidebarToggleState();
    }

    if (sidebar && desktopToggle) {
        desktopToggle.addEventListener('click', function (event) {
            event.preventDefault();
            sidebar.classList.toggle('collapsed');
            localStorage.setItem(
                'studioSidebar',
                sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded'
            );
            syncSidebarToggleState();
        });
    }

    if (sidebar && mobileToggle) {
        mobileToggle.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            sidebar.classList.toggle('show');
        });

        document.addEventListener('click', function (event) {
            if (window.innerWidth > 992) return;
            const clickedInsideSidebar = sidebar.contains(event.target);
            const clickedToggle = mobileToggle.contains(event.target);
            if (!clickedInsideSidebar && !clickedToggle) {
                sidebar.classList.remove('show');
            }
        });
    }

    window.addEventListener('resize', applySidebarStateForViewport);
    applySidebarStateForViewport();

    initActiveMenu();
    initCounters();
    initCharts();
});

// ===============================
// ACTIVE MENU HIGHLIGHT
// ===============================

function initActiveMenu() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('.studio-sidebar a');

    links.forEach((link) => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ===============================
// COUNTER ANIMATION
// ===============================

function initCounters() {
    const counters = document.querySelectorAll('.stat-number');

    counters.forEach((counter) => {
        const target = parseInt(counter.getAttribute('data-target'), 10);
        if (!target) return;

        let count = 0;
        const increment = Math.ceil(target / 50);

        const update = setInterval(() => {
            count += increment;

            if (count >= target) {
                counter.innerText = target;
                clearInterval(update);
            } else {
                counter.innerText = count;
            }
        }, 30);
    });
}

// ===============================
// CHART INITIALIZATION
// ===============================

function initCharts() {
    const revenueChart = document.getElementById('revenueChart');
    if (!revenueChart || typeof Chart === 'undefined') return;

    new Chart(revenueChart, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [
                {
                    label: 'Revenue',
                    data: [12000, 19000, 15000, 22000, 28000, 30000],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99,102,241,0.2)',
                    tension: 0.4,
                    fill: true,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#fff',
                    },
                },
            },
            scales: {
                x: {
                    ticks: { color: '#cbd5e1' },
                },
                y: {
                    ticks: { color: '#cbd5e1' },
                },
            },
        },
    });
}
