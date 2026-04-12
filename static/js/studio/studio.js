// ===============================
// STUDIO DASHBOARD JS
// ===============================

document.addEventListener("DOMContentLoaded", function () {

    initSidebar();
    initActiveMenu();
    initCounters();
    initCharts();
    handleResize();

});


// ===============================
// SIDEBAR TOGGLE
// ===============================

function toggleStudioSidebar() {
    const sidebar = document.getElementById("studioSidebar");
    if (!sidebar) return;

    sidebar.classList.toggle("collapsed");

    // Save state in localStorage
    const collapsed = sidebar.classList.contains("collapsed");
    localStorage.setItem("studioSidebarCollapsed", collapsed);
}

// Restore sidebar state
function initSidebar() {
    const sidebar = document.getElementById("studioSidebar");
    if (!sidebar) return;

    const savedState = localStorage.getItem("studioSidebarCollapsed");
    if (savedState === "true") {
        sidebar.classList.add("collapsed");
    }
}

// Auto close on mobile click
document.addEventListener("click", function (e) {
    const sidebar = document.getElementById("studioSidebar");

    if (!sidebar) return;

    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && sidebar.classList.contains("collapsed") === false) {
            sidebar.classList.add("collapsed");
        }
    }
});


// ===============================
// ACTIVE MENU HIGHLIGHT
// ===============================

function initActiveMenu() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll(".studio-sidebar a");

    links.forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
}


// ===============================
// COUNTER ANIMATION
// ===============================

function initCounters() {
    const counters = document.querySelectorAll(".stat-number");

    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute("data-target"));
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
    if (document.body && document.body.classList.contains('studio-dashboard-page')) {
        return;
    }

    const revenueChart = document.getElementById("revenueChart");
    if (revenueChart && typeof Chart !== "undefined") {

        new Chart(revenueChart, {
            type: 'line',
            data: {
                labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
                datasets: [{
                    label: "Revenue",
                    data: [12000, 19000, 15000, 22000, 28000, 30000],
                    borderColor: "#6366f1",
                    backgroundColor: "rgba(99,102,241,0.2)",
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: "#fff"
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: "#cbd5e1" }
                    },
                    y: {
                        ticks: { color: "#cbd5e1" }
                    }
                }
            }
        });
    }
}


// ===============================
// WINDOW RESIZE HANDLING
// ===============================

function handleResize() {
    window.addEventListener("resize", function () {
        const sidebar = document.getElementById("studioSidebar");

        if (!sidebar) return;

        if (window.innerWidth > 768) {
            sidebar.classList.remove("collapsed");
        }
    });
}
