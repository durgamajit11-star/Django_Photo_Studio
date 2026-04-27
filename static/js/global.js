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

(function () {
    function loadScriptOnce(src) {
        if (!src || document.querySelector('script[data-lazy-src="' + src + '"]')) {
            return;
        }

        const script = document.createElement('script');
        script.src = src;
        script.defer = true;
        script.dataset.lazySrc = src;
        document.body.appendChild(script);
    }

    function scheduleIdle(callback) {
        if ('requestIdleCallback' in window) {
            window.requestIdleCallback(callback, { timeout: 1500 });
            return;
        }

        window.setTimeout(callback, 350);
    }

    function lazyLoadChatbotScript() {
        const container = document.getElementById('chatbot-container');
        if (!container) {
            return;
        }

        const scriptSrc = container.dataset.chatbotScript;
        scheduleIdle(function () {
            loadScriptOnce(scriptSrc);
        });
    }

    document.addEventListener('DOMContentLoaded', lazyLoadChatbotScript);
})();

(function () {
    const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const REVEAL_SELECTOR = [
        'section',
        '.glass-panel',
        '.panel-section',
        '.card',
        '.dashboard-card',
        '.admin-panel',
        '.studio-card',
        '.stat-card',
        '.mini-item',
        '.notification-item',
        '.pay-card',
        '.receipt-card',
    ].join(', ');

    let revealObserver = null;

    function shouldAnimate() {
        return !reduceMotionQuery.matches;
    }

    function markRevealTargets(scope) {
        if (!shouldAnimate()) {
            return;
        }

        const root = scope && scope.nodeType === 1 ? scope : document;
        const targets = root.querySelectorAll(REVEAL_SELECTOR);

        targets.forEach(function (el, index) {
            if (el.dataset.uiRevealReady === '1') {
                return;
            }

            el.dataset.uiRevealReady = '1';
            el.classList.add('ui-reveal');
            el.style.setProperty('--ui-reveal-delay', String(Math.min((index % 8) * 40, 280)) + 'ms');

            if (revealObserver) {
                revealObserver.observe(el);
            } else {
                el.classList.add('is-visible');
            }
        });
    }

    function initObserver() {
        if (!('IntersectionObserver' in window) || !shouldAnimate()) {
            return;
        }

        revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) {
                    return;
                }

                entry.target.classList.add('is-visible');
                revealObserver.unobserve(entry.target);
            });
        }, {
            threshold: 0.08,
            rootMargin: '0px 0px -6% 0px',
        });
    }

    function watchDynamicDom() {
        if (!('MutationObserver' in window) || !shouldAnimate()) {
            return;
        }

        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (node.nodeType !== 1) {
                        return;
                    }
                    markRevealTargets(node);
                });
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    }

    function initUiMotion() {
        initObserver();
        markRevealTargets(document);
        watchDynamicDom();
    }

    document.addEventListener('DOMContentLoaded', initUiMotion);
})();

(function () {
    function shouldTrackVitals() {
        const params = new URLSearchParams(window.location.search);
        const byQuery = params.get('perf') === '1';
        const byStorage = localStorage.getItem('studiosync_perf_debug') === '1';
        return byQuery || byStorage;
    }

    function safeSend(url, payload) {
        if (!url) {
            return;
        }

        const body = JSON.stringify(payload);
        if (navigator.sendBeacon) {
            const blob = new Blob([body], { type: 'application/json' });
            navigator.sendBeacon(url, blob);
            return;
        }

        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: body,
            keepalive: true,
            credentials: 'same-origin',
        }).catch(function () {
            // Ignore telemetry transport errors.
        });
    }

    function initWebVitalsTracking() {
        if (!shouldTrackVitals() || !('PerformanceObserver' in window)) {
            return;
        }

        const vitals = {
            path: window.location.pathname,
            lcp: 0,
            cls: 0,
            inp: 0,
            fcp: 0,
        };

        try {
            const fcpObserver = new PerformanceObserver(function (entryList) {
                const entries = entryList.getEntries();
                const last = entries[entries.length - 1];
                if (last) {
                    vitals.fcp = Math.round(last.startTime);
                }
            });
            fcpObserver.observe({ type: 'paint', buffered: true });
        } catch (error) {
            // FCP observer unsupported.
        }

        try {
            const lcpObserver = new PerformanceObserver(function (entryList) {
                const entries = entryList.getEntries();
                const last = entries[entries.length - 1];
                if (last) {
                    vitals.lcp = Math.round(last.startTime);
                }
            });
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (error) {
            // LCP observer unsupported.
        }

        try {
            let clsValue = 0;
            const clsObserver = new PerformanceObserver(function (entryList) {
                entryList.getEntries().forEach(function (entry) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                });
                vitals.cls = Number(clsValue.toFixed(4));
            });
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (error) {
            // CLS observer unsupported.
        }

        try {
            const inpObserver = new PerformanceObserver(function (entryList) {
                entryList.getEntries().forEach(function (entry) {
                    const candidate = entry.duration || 0;
                    if (candidate > vitals.inp) {
                        vitals.inp = Math.round(candidate);
                    }
                });
            });
            inpObserver.observe({ type: 'event', buffered: true, durationThreshold: 40 });
        } catch (error) {
            // INP observer unsupported.
        }

        function flushVitals() {
            const payload = {
                ...vitals,
                ts: Date.now(),
            };

            console.info('[StudioSync][WebVitals]', payload);

            const endpoint = document.body.dataset.perfEndpoint || '';
            safeSend(endpoint, payload);
        }

        window.addEventListener('visibilitychange', function () {
            if (document.visibilityState === 'hidden') {
                flushVitals();
            }
        });

        window.addEventListener('pagehide', flushVitals);
    }

    document.addEventListener('DOMContentLoaded', initWebVitalsTracking);
})();
