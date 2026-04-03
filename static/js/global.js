(function () {
    const STORAGE_KEY = 'studiosync_theme';

    function getSavedTheme() {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'light' || saved === 'dark') {
            return saved;
        }
        return 'dark';
    }

    function applyTheme(theme) {
        const root = document.documentElement;
        root.setAttribute('data-theme', theme);
        root.setAttribute('data-bs-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);
        updateToggleButtons(theme);
        document.dispatchEvent(new CustomEvent('studiosync:theme-changed', { detail: { theme: theme } }));
    }

    function updateToggleButtons(theme) {
        const toggles = document.querySelectorAll('[data-theme-toggle]');
        toggles.forEach(function (btn) {
            const icon = btn.querySelector('[data-theme-icon]');
            const text = btn.querySelector('[data-theme-text]');

            if (icon) {
                icon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
            }
            if (text) {
                text.textContent = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
            }
            btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
            btn.setAttribute('title', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
        });
    }

    function toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme') || getSavedTheme();
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
    }

    function initializeTheme() {
        applyTheme(getSavedTheme());
    }

    window.StudioSyncTheme = {
        applyTheme: applyTheme,
        toggleTheme: toggleTheme,
        initializeTheme: initializeTheme,
    };

    window.toggleTheme = toggleTheme;

    document.addEventListener('DOMContentLoaded', function () {
        initializeTheme();

        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                toggleTheme();
            });
        });
    });
})();
