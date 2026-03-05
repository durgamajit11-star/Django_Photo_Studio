/* ===============================
   StudioSync Admin Panel JS
   =============================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ===============================
       Sidebar Collapse / Expand
    =============================== */

    const sidebar = document.querySelector(".admin-sidebar");
    const wrapper = document.querySelector(".admin-wrapper");
    const toggleBtn = document.querySelector("#sidebarToggle");

    // Load saved sidebar state
    if (localStorage.getItem("adminSidebar") === "collapsed") {
        sidebar.classList.add("collapsed");
        wrapper.classList.add("collapsed");
    }

    // Toggle sidebar
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
            wrapper.classList.toggle("collapsed");

            // Save state
            if (sidebar.classList.contains("collapsed")) {
                localStorage.setItem("adminSidebar", "collapsed");
            } else {
                localStorage.setItem("adminSidebar", "expanded");
            }
        });
    }

    /* ===============================
       Auto Highlight Active Link
    =============================== */

    const currentUrl = window.location.href;
    const sidebarLinks = document.querySelectorAll(".admin-sidebar a");

    sidebarLinks.forEach(link => {
        if (link.href === currentUrl) {
            link.classList.add("active");
        }
    });

    /* ===============================
       Mobile Sidebar Toggle
    =============================== */

    const mobileToggle = document.querySelector("#mobileSidebarToggle");

    if (mobileToggle) {
        mobileToggle.addEventListener("click", function () {
            sidebar.classList.toggle("mobile-show");
        });
    }

    /* ===============================
       Revenue Chart Initialization
    =============================== */

    const revenueChartCanvas = document.getElementById("revenueChart");

    if (revenueChartCanvas) {

        // Safely load data from json_script
        const labelsElement = document.getElementById("revenue-labels");
        const dataElement = document.getElementById("revenue-data");

        if (labelsElement && dataElement) {

            const revenueLabels = JSON.parse(labelsElement.textContent);
            const revenueData = JSON.parse(dataElement.textContent);

            new Chart(revenueChartCanvas, {
                type: "bar",
                data: {
                    labels: revenueLabels,
                    datasets: [{
                        label: "Revenue (₹)",
                        data: revenueData,
                        backgroundColor: "rgba(79, 70, 229, 0.7)",
                        borderRadius: 6,
                        hoverBackgroundColor: "rgba(99, 102, 241, 0.9)"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: "#1e293b",
                            titleColor: "#ffffff",
                            bodyColor: "#ffffff"
                        }
                    },
                    scales: {
                        x: {
                            ticks: {
                                color: "#cbd5e1"
                            },
                            grid: {
                                color: "rgba(255,255,255,0.05)"
                            }
                        },
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: "#cbd5e1"
                            },
                            grid: {
                                color: "rgba(255,255,255,0.05)"
                            }
                        }
                    }
                }
            });
        }
    }

    /* ===============================
       Smooth Resize Fix
    =============================== */

    window.addEventListener("resize", function () {
        const charts = Chart.instances;
        for (let key in charts) {
            charts[key].resize();
        }
    });

});

