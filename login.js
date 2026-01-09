let currentRole = 'hospital'; 

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

async function handleLogin(event) {
    event.preventDefault(); 

    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;

    try {
        // Pointing to your specific Backend IP
        const response = await fetch("http://172.16.45.110:5000/login", {
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
            // MAKE SURE THESE FILENAMES MATCH YOUR ACTUAL FILES
            window.location.href = currentRole === 'hospital' ? "hospital-dashboard.html" : "seller-dashboard.html";
        } else {
            alert("Invalid Credentials!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Server Unreachable. Check IP 172.16.45.110 and Port 5000.");
    }
}

function togglePassword() {
    const passField = document.getElementById('password');
    passField.type = passField.type === 'password' ? 'text' : 'password';
}
