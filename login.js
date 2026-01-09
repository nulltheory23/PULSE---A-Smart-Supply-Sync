let currentRole = "hospital"; // default

function switchLogin(type) {
  const slider = document.getElementById("toggleSlider");
  const options = document.querySelectorAll(".toggle-option");

  options.forEach(opt => opt.classList.remove("active"));

  if (type === "hospital") {
    slider.style.left = "0%";
    options[0].classList.add("active");
    currentRole = "hospital";
  } else {
    slider.style.left = "50%";
    options[1].classList.add("active");
    currentRole = "seller";
  }
}

/* PASSWORD VISIBILITY */
function togglePassword() {
  const passwordInput = document.getElementById("password");
  const icon = event.target;

  if (passwordInput.type === "password") {
    passwordInput.type = "text";
    icon.classList.replace("fa-eye", "fa-eye-slash");
  } else {
    passwordInput.type = "password";
    icon.classList.replace("fa-eye-slash", "fa-eye");
  }
}

/* ROLE-BASED LOGIN HANDLER */
function handleLogin(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const rememberMe = document.getElementById("remember").checked;

  // Decide API based on role
  let apiEndpoint = "";

  if (currentRole === "hospital") {
    apiEndpoint = "/api/hospital/login"; // future hospital DB
  } else {
    apiEndpoint = "/api/seller/login"; // future seller DB
  }

  console.log("Logging in as:", currentRole);
  console.log("API Endpoint:", apiEndpoint);
  console.log("Username:", username);
  console.log("Remember Me:", rememberMe);

  /*
    FUTURE BACKEND CALL (ENABLE LATER)

    fetch(apiEndpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href =
          currentRole === "hospital"
          ? "hospital-dashboard.html"
          : "seller-dashboard.html";
      } else {
        alert("Invalid credentials");
      }
    });
  */

  // TEMP SUCCESS FOR DEMO
  if (currentRole === "hospital") {
    window.location.href = "hospital-dashboard.html";
  } else {
    window.location.href = "seller-dashboard.html";
  }
}
