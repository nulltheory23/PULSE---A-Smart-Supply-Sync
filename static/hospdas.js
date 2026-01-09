fetch("/api/hospitals")
  .then(res => res.json())
  .then(data => {
    const dashboard = document.getElementById("dashboard");

    data.forEach(hospital => {
      const card = document.createElement("div");
      card.className = "hospital-card";

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

        <button class="request-btn">
          Request Supplies
        </button>
      `;

      dashboard.appendChild(card);
    });
  });
