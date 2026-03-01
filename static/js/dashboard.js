// ===== SIDEBAR TOGGLE =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (!sidebar) return;

    if (window.innerWidth <= 992) {
        sidebar.classList.toggle('show');   // mobile slide
        // Prevent body scroll when sidebar is open
        if (sidebar.classList.contains('show')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }
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
    if (!sidebar) return;
    
    if (window.innerWidth > 992) {
        sidebar.classList.remove('show');
        document.body.style.overflow = 'auto';
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
    const body = document.body;
    body.classList.toggle("light-mode");

    // Save theme in localStorage
    if (body.classList.contains("light-mode")) {
        localStorage.setItem("theme", "light");
    } else {
        localStorage.setItem("theme", "dark");
    }
}

// Load saved theme on page load
document.addEventListener("DOMContentLoaded", function () {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        document.body.classList.add("light-mode");
    }
});


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

// ===== CHAT FUNCTIONALITY =====
function toggleChat() {
    const chatWindow = document.getElementById("chatWindow");
    if (chatWindow) {
        chatWindow.classList.toggle("active");
        // Move chat window to top when opened on mobile
        if (window.innerWidth <= 576 && chatWindow.classList.contains("active")) {
            chatWindow.style.bottom = 'auto';
            chatWindow.style.top = '70px';
        }
    }
}

function sendMessage() {
    const input = document.getElementById("chatInput");
    const chatBody = document.getElementById("chatBody");
    const message = input?.value.trim();

    if (!message) return;

    // User message
    const userMsg = document.createElement("div");
    userMsg.className = "user-message";
    userMsg.innerText = message;
    chatBody?.appendChild(userMsg);

    input.value = "";
    if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;

    // Bot reply simulation with improved responses
    setTimeout(() => {
        const botMsg = document.createElement("div");
        botMsg.className = "bot-message";

        const lowerMessage = message.toLowerCase();

        if (lowerMessage.includes("booking") || lowerMessage.includes("book")) {
            botMsg.innerText = "📅 You can book a studio from the 'Browse Studios' section. Select your preferred date and studio to proceed.";
        } else if (lowerMessage.includes("price") || lowerMessage.includes("cost")) {
            botMsg.innerText = "💰 Our packages start from ₹5,000 onwards. Premium studios may cost more. Use the price filter to find options within your budget.";
        } else if (lowerMessage.includes("help") || lowerMessage.includes("support")) {
            botMsg.innerText = "🆘 I'm here to help! You can ask me about bookings, pricing, studios, or any other questions. How can I assist you?";
        } else if (lowerMessage.includes("studio") || lowerMessage.includes("find")) {
            botMsg.innerText = "🔍 You can browse studios using our search filters. Filter by city, type, rating, and price range to find the perfect studio.";
        } else if (lowerMessage.includes("hi") || lowerMessage.includes("hello")) {
            botMsg.innerText = "👋 Hello! Welcome to StudioSync. How can I help you today?";
        } else {
            botMsg.innerText = "✅ Thank you for your message. Our team will assist you shortly. Is there anything else I can help with?";
        }

        chatBody?.appendChild(botMsg);
        if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;

    }, 600);
}

// Allow Enter key to send message
const chatInput = document.getElementById("chatInput");
if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

// ===== SMOOTH SCROLL ANIMATION =====
document.addEventListener('DOMContentLoaded', () => {
    animateCounters();

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

