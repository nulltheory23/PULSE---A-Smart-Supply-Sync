document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});

async function loadDashboard() {
    try {
        // 1. Fetch data from our APIs
        const [hospRes, sellerRes] = await Promise.all([
            fetch("/api/hospitals"),
            fetch("/ledger") // We use the ledger/inventory endpoint
        ]);

        const hospitals = await hospRes.json();
        
        // Note: For a hackathon, we'll fetch from a new endpoint we need in app.py
        const inventoryRes = await fetch("/api/get-all-inventory");
        const sellerStock = await inventoryRes.json();

        renderMyInventory(hospitals);
        renderSuppliers(sellerStock);

    } catch (err) {
        console.error("Dashboard Error:", err);
    }
}

// Shows the logged in hospital's own stock
function renderMyInventory(allHospitals) {
    const container = document.getElementById("my-stock-content");
    // In a real app, we'd filter by session. For now, let's show the first one as "Mine"
    const myData = allHospitals[0]; 
    
    document.getElementById("user-display").innerText = `Connected: ${myData.name}`;

    let html = "<ul style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; list-style: none;'>";
    for (const [item, qty] of Object.entries(myData.inventory)) {
        html += `<li>${item}: <strong style="color: #00fff5;">${qty}</strong></li>`;
    }
    html += "</ul>";
    container.innerHTML = html;
}

// Shows Seller stock from the Database
function renderSuppliers(suppliers) {
    const container = document.getElementById("supplier-list");
    container.innerHTML = "";

    if (suppliers.length === 0) {
        container.innerHTML = "<p>No active suppliers found in database.</p>";
        return;
    }

    suppliers.forEach(s => {
        const card = document.createElement("div");
        card.className = "hospital-card";
        card.innerHTML = `
            <h2><i class="fas fa-truck-field"></i> ${s.seller_name}</h2>
            <div class="inventory">
                <p>Item: <strong style="color: #fbbf24;">${s.item}</strong></p>
                <p>Available: <strong id="stock-${s.id}">${s.qty}</strong> units</p>
            </div>
            <div style="margin-top: 15px; display: flex; gap: 10px;">
                <input type="number" id="req-qty-${s.id}" value="1" min="1" max="${s.qty}" 
                       style="width: 60px; padding: 5px; border-radius: 5px; background: #1e293b; color: white; border: 1px solid #00fff5;">
                <button class="request-btn" style="margin-top:0;" onclick="makePurchase(${s.id}, '${s.item}', ${s.qty})">
                    Order Now
                </button>
            </div>
        `;
        container.appendChild(card);
    });
}

async function makePurchase(id, itemName, maxQty) {
    const qtyInput = document.getElementById(`req-qty-${id}`);
    const requestedQty = parseInt(qtyInput.value);

    // 🔹 LOGIC: Prevent requesting more than available
    if (requestedQty > maxQty) {
        alert(`❌ Error: Only ${maxQty} units available!`);
        return;
    }

    const response = await fetch("/hospital/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            hospital: "My Hospital", // This would be dynamic from session
            item: itemName,
            qty: requestedQty
        })
    });

    const result = await response.json();
    if (result.status === "Matched") {
        alert(`✅ Success! Order confirmed. Hash: ${result.hash.substring(0,10)}`);
        location.reload(); // Refresh to show updated stock
    } else {
        alert("Transaction pending or failed.");
    }
}