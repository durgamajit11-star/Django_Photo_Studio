function getCsrfToken() {
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (tokenInput) {
        return tokenInput.value;
    }

    const cookies = document.cookie ? document.cookie.split(';') : [];
    for (let i = 0; i < cookies.length; i += 1) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('csrftoken=')) {
            return decodeURIComponent(cookie.substring('csrftoken='.length));
        }
    }
    return '';
}

function toggleEdit(showForm) {
    const profileForm = document.getElementById('profileForm');
    const profileDisplay = document.getElementById('profileDisplay');

    if (!profileForm || !profileDisplay) {
        return;
    }

    if (showForm) {
        profileForm.classList.add('active');
        profileDisplay.style.display = 'none';
    } else {
        profileForm.classList.remove('active');
        profileDisplay.style.display = 'grid';
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function showStatus(message, type) {
    const profileContainer = document.querySelector('.profile-container');
    if (!profileContainer) {
        return;
    }

    const existing = document.getElementById('profileStatusAlert');
    if (existing) {
        existing.remove();
    }

    const alert = document.createElement('div');
    alert.id = 'profileStatusAlert';
    alert.className = `alert ${type === 'error' ? 'alert-danger' : 'alert-success'} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

    profileContainer.prepend(alert);

    window.setTimeout(() => {
        if (alert && alert.parentElement) {
            alert.remove();
        }
    }, 3500);
}

async function postAction(url, payload) {
    const csrf = getCsrfToken();
    const formData = new FormData();

    Object.keys(payload).forEach((key) => {
        formData.append(key, payload[key]);
    });

    const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrf,
        },
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
        throw new Error(data.message || 'Request failed. Please try again.');
    }

    return data;
}

async function savePreferences(event) {
    event.preventDefault();

    const darkThemeToggle = document.getElementById('darkTheme');
    const emailNotifToggle = document.getElementById('emailNotif');
    const smsAlertsToggle = document.getElementById('smsAlerts');
    const marketingToggle = document.getElementById('marketing');

    const payload = {
        action: 'save_preferences',
        email_notifications: String(!!(emailNotifToggle && emailNotifToggle.checked)),
        sms_alerts: String(!!(smsAlertsToggle && smsAlertsToggle.checked)),
        marketing_emails: String(!!(marketingToggle && marketingToggle.checked)),
        dark_theme: String(!!(darkThemeToggle && darkThemeToggle.checked)),
    };

    try {
        const result = await postAction(window.location.pathname, payload);
        showStatus(result.message || 'Preferences saved successfully.');
    } catch (error) {
        showStatus(error.message, 'error');
    }
}

async function logoutAllDevices() {
    const logoutAllBtn = document.getElementById('logoutAllBtn');
    if (logoutAllBtn && logoutAllBtn.disabled) {
        return;
    }

    const confirmed = window.confirm('Logout from all other devices? Your current session will remain active.');
    if (!confirmed) {
        return;
    }

    const logoutUrl = (logoutAllBtn && logoutAllBtn.dataset && logoutAllBtn.dataset.url) || '/dashboard/profile/logout-all/';

    try {
        const result = await postAction(logoutUrl, {});
        showStatus(result.message || 'Logged out from other devices.');
    } catch (error) {
        showStatus(error.message, 'error');
    }
}

async function deleteAccount() {
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    if (deleteAccountBtn && deleteAccountBtn.disabled) {
        return;
    }

    const confirmed = window.confirm('Delete account permanently? This cannot be undone.');
    if (!confirmed) {
        return;
    }

    const deleteUrl = (deleteAccountBtn && deleteAccountBtn.dataset && deleteAccountBtn.dataset.url) || '/dashboard/profile/delete-account/';

    try {
        const result = await postAction(deleteUrl, {});
        if (result.redirect_url) {
            window.location.href = result.redirect_url;
            return;
        }
        showStatus('Account deleted successfully.');
    } catch (error) {
        showStatus(error.message, 'error');
    }
}

function setupProfileImageUpload() {
    const uploadBtn = document.getElementById('triggerUploadBtn');
    const fileInput = document.querySelector('input[name="profile_image"]');

    if (!uploadBtn || !fileInput) {
        return;
    }

    uploadBtn.addEventListener('click', () => fileInput.click());
}

function setupThemePreference() {
    const darkThemeToggle = document.getElementById('darkTheme');
    if (!darkThemeToggle) {
        return;
    }

    darkThemeToggle.addEventListener('change', function () {
        const nextTheme = this.checked ? 'dark' : 'light';
        if (window.StudioSyncTheme && typeof window.StudioSyncTheme.applyTheme === 'function') {
            window.StudioSyncTheme.applyTheme(nextTheme);
        }
    });

    document.addEventListener('studiosync:theme-changed', function (event) {
        if (event && event.detail && event.detail.theme) {
            darkThemeToggle.checked = event.detail.theme === 'dark';
        }
    });
}

function setSectionExpanded(card, body, button, expanded) {
    if (!card || !body || !button) {
        return;
    }

    const icon = button.querySelector('i');
    card.classList.toggle('is-collapsed', !expanded);
    body.hidden = !expanded;
    button.setAttribute('aria-expanded', String(expanded));

    if (icon) {
        icon.className = expanded ? 'bi bi-chevron-up' : 'bi bi-chevron-down';
    }
}

function setupSectionToggles() {
    const toggleButtons = document.querySelectorAll('[data-toggle-card]');

    toggleButtons.forEach((button) => {
        const targetId = button.getAttribute('data-target');
        const body = targetId ? document.getElementById(targetId) : null;
        const card = button.closest('.profile-card');
        const initiallyExpanded = button.getAttribute('aria-expanded') === 'true';

        if (!card || !body) {
            return;
        }

        setSectionExpanded(card, body, button, initiallyExpanded);

        button.addEventListener('click', function () {
            const expanded = button.getAttribute('aria-expanded') === 'true';
            setSectionExpanded(card, body, button, !expanded);
        });
    });
}

function updateDangerActionsState() {
    const acknowledge = document.getElementById('dangerAcknowledge');
    const deleteConfirmInput = document.getElementById('deleteConfirmInput');
    const logoutAllBtn = document.getElementById('logoutAllBtn');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');

    if (!acknowledge) {
        return;
    }

    const acknowledged = !!acknowledge.checked;
    const deleteReady = (deleteConfirmInput && deleteConfirmInput.value || '').trim().toUpperCase() === 'DELETE';

    if (logoutAllBtn) {
        logoutAllBtn.disabled = !acknowledged;
    }

    if (deleteAccountBtn) {
        deleteAccountBtn.disabled = !(acknowledged && deleteReady);
    }
}

document.addEventListener('click', function (event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach((modal) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const editProfileBtn = document.getElementById('editProfileBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const preferencesForm = document.getElementById('preferencesForm');
    const logoutAllBtn = document.getElementById('logoutAllBtn');
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    const scrollToPreferencesBtn = document.getElementById('scrollToPreferencesBtn');
    const dangerAcknowledge = document.getElementById('dangerAcknowledge');
    const deleteConfirmInput = document.getElementById('deleteConfirmInput');

    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function () {
            toggleEdit(true);
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', function () {
            toggleEdit(false);
        });
    }

    if (preferencesForm) {
        preferencesForm.addEventListener('submit', savePreferences);
    }

    if (logoutAllBtn) {
        logoutAllBtn.addEventListener('click', logoutAllDevices);
    }

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', deleteAccount);
    }

    if (scrollToPreferencesBtn) {
        scrollToPreferencesBtn.addEventListener('click', function () {
            const section = document.getElementById('preferencesCard');
            const preferencesBody = document.getElementById('preferencesBody');
            const preferencesToggle = document.querySelector('[data-target="preferencesBody"]');

            if (section && preferencesBody && preferencesToggle) {
                setSectionExpanded(section, preferencesBody, preferencesToggle, true);
            }

            if (section) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    setupProfileImageUpload();
    setupThemePreference();
    setupSectionToggles();

    if (dangerAcknowledge) {
        dangerAcknowledge.addEventListener('change', updateDangerActionsState);
    }

    if (deleteConfirmInput) {
        deleteConfirmInput.addEventListener('input', updateDangerActionsState);
    }

    updateDangerActionsState();
});

window.openModal = openModal;
window.closeModal = closeModal;
