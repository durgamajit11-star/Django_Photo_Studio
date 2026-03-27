
const loginBtn = document.getElementById('loginBtn');
const userBtn = document.getElementById('userBtn');
const studioBtn = document.getElementById('studioBtn');

const loginForm = document.getElementById('loginForm');
const userForm = document.getElementById('userForm');
const studioForm = document.getElementById('studioForm');
const authWrapper = document.querySelector('.auth-wrapper');

function resetActive() {
    loginBtn.classList.remove('active');
    userBtn.classList.remove('active');
    studioBtn.classList.remove('active');
    loginForm.classList.add('d-none');
    userForm.classList.add('d-none');
    studioForm.classList.add('d-none');
}

loginBtn.addEventListener('click', () => {
    resetActive();
    loginBtn.classList.add('active');
    loginForm.classList.remove('d-none');

    authWrapper.classList.remove('studio-active'); // 🔥
});

userBtn.addEventListener('click', () => {
    resetActive();
    userBtn.classList.add('active');
    userForm.classList.remove('d-none');

    authWrapper.classList.remove('studio-active'); // 🔥
});

studioBtn.addEventListener('click', () => {
    resetActive();
    studioBtn.classList.add('active');
    studioForm.classList.remove('d-none');

    authWrapper.classList.add('studio-active'); // 🔥 IMPORTANT
});

// password toggle
function togglePassword() {
    const passwordField = document.querySelector('#loginForm input[type="password"], #loginForm input[type="text"]');
    const icon = document.querySelector('.toggle-password');

    if (passwordField.type === "password") {
        passwordField.type = "text";
        icon.innerHTML = "🙈";
    } else {
        passwordField.type = "password";
        icon.innerHTML = "👁";
    }
}


