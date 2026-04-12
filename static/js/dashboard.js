// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const contentWrapper = document.getElementById('contentWrapper');
    const sidebarToggleIcon = document.getElementById('sidebarToggleIcon');
    if (!sidebar) return;

    const isMobile = window.innerWidth <= 992;

    if (isMobile) {
        sidebar.classList.toggle('show');   // mobile slide
        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('show')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }
        return;
    }

    sidebar.classList.toggle('collapsed');
    document.body.classList.toggle('sidebar-collapsed', sidebar.classList.contains('collapsed'));

    if (contentWrapper) {
        contentWrapper.classList.toggle('sidebar-collapsed', sidebar.classList.contains('collapsed'));
    }

    localStorage.setItem('studiosync_user_sidebar', sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded');

    if (sidebarToggleIcon) {
        sidebarToggleIcon.className = sidebar.classList.contains('collapsed')
            ? 'bi bi-layout-sidebar-inset-reverse'
            : 'bi bi-layout-sidebar-inset';
    }
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function (event) {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('mobileSidebarToggle');

    if (!sidebar || !toggleBtn) return;

    if (window.innerWidth <= 992 &&
        !sidebar.contains(event.target) &&
        !toggleBtn.contains(event.target) &&
        sidebar.classList.contains('show')) {
        sidebar.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
});

// Handle window resize - hide sidebar on desktop
window.addEventListener('resize', function () {
    const sidebar = document.getElementById('sidebar');
    const contentWrapper = document.getElementById('contentWrapper');
    const sidebarToggleIcon = document.getElementById('sidebarToggleIcon');
    if (!sidebar) return;
    
    if (window.innerWidth > 992) {
        sidebar.classList.remove('show');
        document.body.style.overflow = 'auto';

        const persisted = localStorage.getItem('studiosync_user_sidebar');
        if (persisted === 'collapsed') {
            sidebar.classList.add('collapsed');
            document.body.classList.add('sidebar-collapsed');
            contentWrapper?.classList.add('sidebar-collapsed');
            if (sidebarToggleIcon) {
                sidebarToggleIcon.className = 'bi bi-layout-sidebar-inset-reverse';
            }
        } else {
            sidebar.classList.remove('collapsed');
            document.body.classList.remove('sidebar-collapsed');
            contentWrapper?.classList.remove('sidebar-collapsed');
            if (sidebarToggleIcon) {
                sidebarToggleIcon.className = 'bi bi-layout-sidebar-inset';
            }
        }
    }
});

function toggleSubMenu(id) {
    const menu = document.getElementById(id);
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}

function toggleMobileMenu() {
    const menu = document.getElementById('mobileMenu');
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
}

function logout() {
    // Smooth logout transition
    document.body.style.opacity = '0.8';
    setTimeout(() => {
        window.location.href = "{% url 'logout' %}";
    }, 300);
}

// ===== THEME TOGGLE =====
function toggleTheme() {
    if (window.StudioSyncTheme && typeof window.StudioSyncTheme.toggleTheme === 'function') {
        window.StudioSyncTheme.toggleTheme();
    }
}


// ===== FILTER FUNCTION =====
function applyFilters() {
    // Check if filter elements exist
    const cityFilter = document.getElementById('cityFilter');
    const typeFilter = document.getElementById('typeFilter');
    const ratingFilter = document.getElementById('ratingFilter');
    const priceFilter = document.getElementById('priceFilter');

    if (!cityFilter && !typeFilter && !ratingFilter && !priceFilter) {
        // No filters on this page
        return;
    }

    const city = cityFilter?.value.toLowerCase() || '';
    const type = typeFilter?.value || '';
    const rating = ratingFilter?.value || '';
    const price = priceFilter?.value || '';

    const studios = document.querySelectorAll('.studio-item');
    if (studios.length === 0) return;

    let visibleCount = 0;

    studios.forEach(studio => {
        const studioCity = studio.dataset.city || '';
        const studioType = studio.dataset.type || '';
        const studioRating = parseFloat(studio.dataset.rating) || 0;
        const studioPrice = studio.dataset.price || '';

        let visible = true;

        if (city && !studioCity.toLowerCase().includes(city)) visible = false;
        if (type && studioType !== type) visible = false;
        if (rating && studioRating < parseFloat(rating)) visible = false;
        if (price && studioPrice !== price) visible = false;

        studio.style.display = visible ? 'grid' : 'none';
        if (visible) visibleCount++;
    });

    console.log(`Showing ${visibleCount} studios`);
}

// Filter on input - safely attach listeners
const cityFilter = document.getElementById('cityFilter');
if (cityFilter) {
    cityFilter.addEventListener('keyup', applyFilters);
}

const typeFilter = document.getElementById('typeFilter');
if (typeFilter) {
    typeFilter.addEventListener('change', applyFilters);
}

const ratingFilter = document.getElementById('ratingFilter');
if (ratingFilter) {
    ratingFilter.addEventListener('change', applyFilters);
}

const priceFilter = document.getElementById('priceFilter');
if (priceFilter) {
    priceFilter.addEventListener('change', applyFilters);
}

// ===== ANIMATED COUNTERS =====
const animateCounters = () => {
    const counters = document.querySelectorAll(".stat-number");

    if (counters.length === 0) {
        // No counters on this page
        return;
    }

    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.animated) {
                const target = entry.target;
                target.dataset.animated = 'true';

                const finalValue = parseInt(target.innerText) || 0;
                let currentValue = 0;
                const increment = Math.ceil(finalValue / 50);
                const interval = setInterval(() => {
                    if (currentValue >= finalValue) {
                        target.innerText = finalValue;
                        clearInterval(interval);
                    } else {
                        currentValue += increment;
                        target.innerText = Math.min(currentValue, finalValue);
                    }
                }, 30);

                observer.unobserve(target);
            }
        });
    }, observerOptions);

    counters.forEach(counter => observer.observe(counter));
};

// Chatbot behavior is handled by static/js/core/chatbot.js.

// ===== SMOOTH SCROLL ANIMATION =====
document.addEventListener('DOMContentLoaded', () => {
    animateCounters();

    const sidebar = document.getElementById('sidebar');
    const contentWrapper = document.getElementById('contentWrapper');
    const sidebarToggleIcon = document.getElementById('sidebarToggleIcon');

    if (sidebar && window.innerWidth > 992) {
        const persisted = localStorage.getItem('studiosync_user_sidebar');
        if (persisted === 'collapsed') {
            sidebar.classList.add('collapsed');
            document.body.classList.add('sidebar-collapsed');
            contentWrapper?.classList.add('sidebar-collapsed');
            if (sidebarToggleIcon) {
                sidebarToggleIcon.className = 'bi bi-layout-sidebar-inset-reverse';
            }
        }
    }

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// ===== RESIZE LISTENER =====
window.addEventListener('resize', () => {
    // Reset sidebar on resize
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 992) {
        sidebar?.classList.remove('show');
    }
});

