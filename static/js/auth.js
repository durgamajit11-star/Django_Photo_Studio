
const loginBtn = document.getElementById('loginBtn');
const userBtn = document.getElementById('userBtn');
const studioBtn = document.getElementById('studioBtn');

const loginForm = document.getElementById('loginForm');
const userForm = document.getElementById('userForm');
const studioForm = document.getElementById('studioForm');

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
});

userBtn.addEventListener('click', () => {
    resetActive();
    userBtn.classList.add('active');
    userForm.classList.remove('d-none');
});

studioBtn.addEventListener('click', () => {
    resetActive();
    studioBtn.classList.add('active');
    studioForm.classList.remove('d-none');
});
// password toggle
function togglePassword() {
    const passwordField = document.querySelector('#loginForm input[type="password"], #loginForm input[type="text"]');
    if (passwordField.type === "password") {
        passwordField.type = "text";
    } else {
        passwordField.type = "password";
    }
}
