let currentRole = 'hospital'; 

// 1. Fixed the Toggle Logic
function switchLogin(role) {
    currentRole = role;
    const slider = document.getElementById('toggleSlider');
    const options = document.querySelectorAll('.toggle-option');
    
    if (role === 'seller') {
        slider.style.left = '50%';
        options[1].classList.add('active');
        options[0].classList.remove('active');
    } else {
        slider.style.left = '0';
        options[0].classList.add('active');
        options[1].classList.remove('active');
    }
}

// 2. Fixed the Login Logic for Render
async function handleLogin(event) {
    event.preventDefault(); // Prevents page reload

    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    try {
        // CHANGED: Use '/login' instead of the local IP address
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                username: user, 
                password: pass, 
                role: currentRole 
            })
        });

        const result = await response.json();

        if (result.success) {
            // CHANGED: Redirect to the Flask ROUTE, not the .html filename
            // In your app.py, the route for the dashboard is "/dashboard"
            window.location.href = "/dashboard";
        } else {
            alert(result.message || "Invalid Credentials!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Connection failed. The server might still be waking up on Render.");
    }
}

// 3. Simple Password Toggle
function togglePassword() {
    const passField = document.getElementById('password');
    const icon = document.querySelector('.password-field i');
    
    if (passField.type === 'password') {
        passField.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passField.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}