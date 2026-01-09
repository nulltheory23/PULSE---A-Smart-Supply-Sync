fetch("/api/hospitals")
  .then(res => {
    if (!res.ok) throw new Error("Could not fetch hospital data");
    return res.json();
  })
  .then(data => {
    const dashboard = document.getElementById("dashboard");
    
    // Clear any "Loading..." text or hardcoded cards before injecting new ones
    dashboard.innerHTML = ""; 

    data.forEach(hospital => {
      const card = document.createElement("div");
      card.className = "hospital-card";

      // Build the inventory list dynamically
      let inventoryList = "";
      Object.keys(hospital.inventory).forEach(item => {
        inventoryList += `<li>${item}: <strong>${hospital.inventory[item]}</strong></li>`;
      });

      card.innerHTML = `
        <h2>${hospital.name}</h2>
        <p><i class="fas fa-phone"></i> ${hospital.phone}</p>
        <p><i class="fas fa-envelope"></i> ${hospital.email}</p>

        <div class="inventory">
          <h3>Inventory Status</h3>
          <ul>${inventoryList}</ul>
        </div>

        <button class="request-btn" onclick="raiseRequest('${hospital.name}')">
          Request Supplies
        </button>
      `;

      dashboard.appendChild(card);
    });
  })
  .catch(err => {
    console.error("Error loading dashboard:", err);
    document.getElementById("dashboard").innerHTML = "<p>Error loading hospital data. Please try again later.</p>";
  });

// Add the raiseRequest function so the buttons work!
function raiseRequest(hospitalName) {
    alert("Request for " + hospitalName + " sent to suppliers!");
    // In a real app, you'd add another fetch() here to update the DB
}