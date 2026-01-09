document.addEventListener("DOMContentLoaded", loadDashboard);

async function loadDashboard() {
    try {
        const [hospitalRes, sellerRes] = await Promise.all([
            fetch("/api/hospital/me"),
            fetch("/api/sellers")
        ]);

        const hospital = await hospitalRes.json();
        const sellers = await sellerRes.json();

        renderMyInventory(hospital);
        renderSuppliers(sellers);

    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

// --------------------
// HOSPITAL INVENTORY
// --------------------
function renderMyInventory(hospital) {
    document.getElementById("user-display").innerText =
        `Connected: ${hospital.name}`;

    const container = document.getElementById("my-stock-content");

    let html = "<ul style='display:grid;grid-template-columns:1fr 1fr;gap:10px;list-style:none;'>";

    for (let item in hospital.inventory) {
        html += `<li>${item}: <strong style="color:#00fff5">${hospital.inventory[item]}</strong></li>`;
    }

    html += "</ul>";
    container.innerHTML = html;
}

// --------------------
// SELLER INVENTORY
// --------------------
function renderSuppliers(sellers) {
    const container = document.getElementById("supplier-list");
    container.innerHTML = "";

    sellers.forEach(s => {
        const card = document.createElement("div");
        card.className = "hospital-card";

        card.innerHTML = `
            <h2><i class="fas fa-truck"></i> ${s.seller_name}</h2>
            <p>Item: <strong>${s.item}</strong></p>
            <p>Available: <strong>${s.qty}</strong></p>

            <input type="number" id="qty-${s.id}" min="1" max="${s.qty}" value="1">
            <button onclick="orderItem('${s.item}', ${s.qty})">
                Order
            </button>
        `;

        container.appendChild(card);
    });
}

// --------------------
// PLACE ORDER
// --------------------
async function orderItem(item, maxQty) {
    const qty = parseInt(event.target.previousElementSibling.value);

    if (qty > maxQty) {
        alert("❌ Cannot order more than available stock");
        return;
    }

    const res = await fetch("/hospital/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item, qty })
    });

    const data = await res.json();

    if (data.status === "Matched") {
        alert("✅ Order successful!");
        location.reload();
    } else {
        alert("❌ Order failed");
    }
}
