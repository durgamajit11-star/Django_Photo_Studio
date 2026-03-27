/* ===============================
   StudioSync Admin Panel JS
   =============================== */
document.addEventListener("DOMContentLoaded", function () {

    const sidebar = document.querySelector(".admin-sidebar");
    const wrapper = document.querySelector(".admin-wrapper");
    const toggleBtn = document.querySelector("#sidebarToggle");
    const mobileToggle = document.querySelector("#mobileSidebarToggle");

    // Sidebar collapse
    if (localStorage.getItem("adminSidebar") === "collapsed") {
        sidebar.classList.add("collapsed");
        wrapper.classList.add("collapsed");
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("collapsed");
            wrapper.classList.toggle("collapsed");

            localStorage.setItem(
                "adminSidebar",
                sidebar.classList.contains("collapsed") ? "collapsed" : "expanded"
            );
        });
    }

    // Mobile toggle
    if (mobileToggle) {
        mobileToggle.addEventListener("click", function () {
            sidebar.classList.toggle("show"); // ✅ fixed
        });
    }

});

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


