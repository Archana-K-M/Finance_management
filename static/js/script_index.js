const loginTab = document.getElementById('login-tab');
const signupTab = document.getElementById('signup-tab');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const darkModeBtn = document.getElementById('dark-mode-btn');

// Toggle Forms
loginTab.addEventListener('click', () => {
    loginForm.style.display = 'block';
    signupForm.style.display = 'none';
    loginTab.classList.add('active');
    signupTab.classList.remove('active');
});

signupTab.addEventListener('click', () => {
    signupForm.style.display = 'block';
    loginForm.style.display = 'none';
    signupTab.classList.add('active');
    loginTab.classList.remove('active');
});

// Toggle Password Visibility
function setupPasswordToggle(inputId, toggleId) {
    const passwordInput = document.getElementById(inputId);
    const togglePassword = document.getElementById(toggleId);

    togglePassword.addEventListener('click', () => {
        if (passwordInput.type === "password") {
            passwordInput.type = "text";
            togglePassword.textContent = "🙈";
        } else {
            passwordInput.type = "password";
            togglePassword.textContent = "👁";
        }
    });
}

setupPasswordToggle('login-password', 'login-toggle-password');
setupPasswordToggle('signup-password', 'signup-toggle-password');

// Dark Mode
darkModeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
});
// Handle Login Form Submit
document.getElementById('login-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent page reload

    const email = e.target.querySelector('input[type="text"]').value;
    const password = e.target.querySelector('input[type="password"]').value;

    // Send login request to Flask backend
    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: email,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Login successful') {
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            alert(data.message);  // Display error message
        }
    })
    .catch(error => console.error('Error:', error));
});

// Handle Signup Form Submit
document.getElementById('signup-form').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent page reload

    const email = e.target.querySelector('input[type="text"]').value;
    const password = e.target.querySelector('input[type="password"]').value;

    // Send signup request to Flask backend
    fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: email,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'User registered successfully') {
            alert('Signup successful! Now, you can log in.');
            document.getElementById('signup-form').style.display = 'none';
            document.getElementById('login-form').style.display = 'block';
        } else {
            alert(data.message);  // Display error message
        }
    })
    .catch(error => console.error('Error:', error));
});

// Toggle password visibility
document.querySelectorAll('.toggle-password').forEach(toggle => {
    toggle.addEventListener('click', function() {
        const passwordField = this.previousElementSibling;
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
        } else {
            passwordField.type = 'password';
        }
    });
});
