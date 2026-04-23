(function () {
    const STORAGE_KEY = 'studiosync_theme';
    const LOCKED_THEME = 'dark';

    function getSavedTheme() {
        return LOCKED_THEME;
    }

    function applyTheme(theme) {
        const resolvedTheme = LOCKED_THEME;
        const root = document.documentElement;
        root.setAttribute('data-theme', resolvedTheme);
        root.setAttribute('data-bs-theme', resolvedTheme);
        localStorage.setItem(STORAGE_KEY, resolvedTheme);
        updateToggleButtons(resolvedTheme);
        document.dispatchEvent(new CustomEvent('studiosync:theme-changed', { detail: { theme: resolvedTheme } }));
    }

    function updateToggleButtons(theme) {
        const toggles = document.querySelectorAll('[data-theme-toggle]');
        toggles.forEach(function (btn) {
            const icon = btn.querySelector('[data-theme-icon]');
            const text = btn.querySelector('[data-theme-text]');

            if (icon) {
                icon.className = 'bi bi-moon-stars-fill';
            }
            if (text) {
                text.textContent = 'Dark Mode';
            }
            btn.setAttribute('aria-label', 'Dark mode enabled');
            btn.setAttribute('title', 'Dark mode enabled');
        });
    }

    function toggleTheme() {
        applyTheme(LOCKED_THEME);
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
                applyTheme(LOCKED_THEME);
            });
        });
    });
})();
