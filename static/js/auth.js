
document.addEventListener("DOMContentLoaded", function () {
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion) {
        document.body.classList.add("auth-ready");
    } else {
        requestAnimationFrame(function () {
            document.body.classList.add("auth-ready");
        });
    }

    const loginBtn = document.getElementById("loginBtn");
    const userBtn = document.getElementById("userBtn");
    const studioBtn = document.getElementById("studioBtn");

    const loginForm = document.getElementById("loginForm");
    const userForm = document.getElementById("userForm");
    const studioForm = document.getElementById("studioForm");
    const authWrapper = document.querySelector(".auth-wrapper");

    if (!loginBtn || !userBtn || !studioBtn || !loginForm || !userForm || !studioForm) {
        return;
    }

    function resizeTextarea(textarea) {
        if (!textarea) {
            return;
        }

        const minHeight = textarea.dataset.minHeight || window.getComputedStyle(textarea).minHeight;
        textarea.dataset.minHeight = minHeight;

        textarea.style.height = "auto";
        const parsedMinHeight = parseFloat(minHeight) || 0;
        textarea.style.height = Math.max(textarea.scrollHeight, parsedMinHeight) + "px";
    }

    function setupAutoGrowTextareas(scope) {
        const root = scope || document;
        const textareas = root.querySelectorAll("textarea.auto-grow-textarea");

        textareas.forEach(function (textarea) {
            if (!textarea.dataset.autogrowBound) {
                textarea.addEventListener("input", function () {
                    resizeTextarea(textarea);
                });
                textarea.dataset.autogrowBound = "1";
            }
            resizeTextarea(textarea);
        });
    }

    function showForm(type) {
        loginForm.classList.add("d-none");
        userForm.classList.add("d-none");
        studioForm.classList.add("d-none");

        loginForm.setAttribute("aria-hidden", "true");
        userForm.setAttribute("aria-hidden", "true");
        studioForm.setAttribute("aria-hidden", "true");

        loginBtn.classList.remove("active");
        userBtn.classList.remove("active");
        studioBtn.classList.remove("active");

        loginBtn.setAttribute("aria-selected", "false");
        userBtn.setAttribute("aria-selected", "false");
        studioBtn.setAttribute("aria-selected", "false");

        if (type === "login") {
            loginForm.classList.remove("d-none");
            loginBtn.classList.add("active");
            loginBtn.setAttribute("aria-selected", "true");
            loginForm.setAttribute("aria-hidden", "false");
        } else if (type === "user") {
            userForm.classList.remove("d-none");
            userBtn.classList.add("active");
            userBtn.setAttribute("aria-selected", "true");
            userForm.setAttribute("aria-hidden", "false");
        } else {
            studioForm.classList.remove("d-none");
            studioBtn.classList.add("active");
            studioBtn.setAttribute("aria-selected", "true");
            studioForm.setAttribute("aria-hidden", "false");
            setupAutoGrowTextareas(studioForm);
        }

        if (authWrapper) {
            authWrapper.setAttribute("data-active-tab", type);
        }
    }

    loginBtn.addEventListener("click", function () {
        showForm("login");
    });

    userBtn.addEventListener("click", function () {
        showForm("user");
    });

    studioBtn.addEventListener("click", function () {
        showForm("studio");
    });

    const urlRole = new URLSearchParams(window.location.search).get("role");
    const tabFromRole = urlRole === "studio" ? "studio" : (urlRole === "user" ? "user" : null);
    const initialTab = tabFromRole || (authWrapper && authWrapper.dataset.activeTab) || "login";
    const normalizedTab = ["login", "user", "studio"].includes(initialTab) ? initialTab : "login";
    showForm(normalizedTab);
    setupAutoGrowTextareas(studioForm);
});

function togglePassword() {
    const pwd = document.getElementById("id_password");
    const toggleIcon = document.querySelector(".toggle-password i");
    if (!pwd) {
        return;
    }
    const isHidden = pwd.type === "password";
    pwd.type = isHidden ? "text" : "password";
    if (toggleIcon) {
        toggleIcon.className = isHidden ? "bi bi-eye-slash" : "bi bi-eye";
    }
}


