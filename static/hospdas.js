document.addEventListener("DOMContentLoaded", () => {
    // Run both functions when page loads
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // 1. Fetch My Profile & 2. Fetch Market Supplies
        await Promise.all([
            fetchMyProfile(),
            fetchMarketplace()
        ]);
    } catch (error) {
        console.error("Critical Dashboard Error:", error);
    }
}

async function fetchMyProfile() {
    try {
        const res = await fetch("/api/hospital/profile");
        if (!res.ok) throw new Error("Profile fetch failed");
        
        const data = await res.json();
        
        // Update Header
        const userTag = document.getElementById("user-tag");
        const hospTitle = document.getElementById("hosp-title");
        
        if (userTag) userTag.innerText = data.display_name || "User";
        if (hospTitle) hospTitle.innerText = `${data.display_name || "Hospital"} Portal`;

        // Update Inventory List
        const container = document.getElementById("my-stock");
        if (!container) return;

        if (!data.inventory || Object.keys(data.inventory).length === 0) {
            container.innerHTML = "<p>No local stock recorded.</p>";
            return;
        }

        let html = "<ul style='list-style: none; padding: 0;'>";
        for (const [item, qty] of Object.entries(data.inventory)) {
            const statusColor = qty < 10 ? "#ef4444" : "#00fff5";
            html += `<li style="padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        ${item}: <strong style="color: #00fff5;">${qty}</strong>
                     </li>`;
        }
        html += "</ul>";
        container.innerHTML = html;

    } catch (err) {
        console.error("Profile Error:", err);
        const container = document.getElementById("my-stock");
        if (container) container.innerHTML = "<p style='color: #ff4444;'>Error loading profile.</p>";
    }
}

async function fetchMarketplace() {
    try {
        const res = await fetch("/api/sellers");
        if (!res.ok) throw new Error("Sellers fetch failed");
        
        const items = await res.json();
        const container = document.getElementById("market-list");
        if (!container) return;

        container.innerHTML = "";

        if (!items || items.length === 0) {
            container.innerHTML = "<p style='text-align: center; color: #94a3b8;'>No supplies currently available from sellers.</p>";
            return;
        }

        items.forEach(i => {
            const card = document.createElement("div");
            card.className = "hospital-card";
            card.style.marginBottom = "15px";
            
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div style="flex: 1;">
                        <h2 style="color: #fbbf24; margin: 0;">${i.item}</h2>
                        <p style="margin: 5px 0; font-size: 0.85rem; color: #94a3b8;">Supplier: ${i.seller_name}</p>
                        <p style="margin: 0;">Available: <strong id="stock-${i.id}" style="color: #00fff5;">${i.qty}</strong></p>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
                        <input type="number" id="qty-${i.id}" value="1" min="1" max="${i.qty}" 
                               style="width: 60px; padding: 8px; background: #1e293b; color: white; border: 1px solid #334155; border-radius: 8px;">
                        <button class="request-btn" onclick="buyItem('${i.item}', ${i.id})" style="margin: 0; padding: 8px 15px;">
                            Order
                        </button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error("Marketplace Error:", err);
        const container = document.getElementById("market-list");
        if (container) container.innerHTML = "<p style='color: #ff4444;'>Error loading market data.</p>";
    }
}

async function buyItem(itemName, id) {
    const qtyInput = document.getElementById(`qty-${id}`);
    const qty = parseInt(qtyInput.value);

    if (isNaN(qty) || qty <= 0) {
        alert("Please enter a valid quantity.");
        return;
    }

    try {
        const res = await fetch("/hospital/request", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ item: itemName, qty: qty })
        });
        
        const result = await res.json();
        
        if (result.status === "Matched") {
            alert(`✅ Order Successful!\nTransaction Hash: ${result.hash.substring(0,20)}...`);
            // Refresh data to show new stock levels
            loadDashboardData();
        } else {
            alert("❌ Order Failed: Insufficient stock or supplier unavailable.");
        }
    } catch (err) {
        console.error("Purchase Error:", err);
        alert("Connection error. Could not process order.");
    }
}


async function fetchMyOrders() {
    const res = await fetch("/ledger");
    const allTx = await res.json();
    const container = document.getElementById("my-orders");
    
    // Filter to only show orders for 'My Hospital' (or current logged user)
    const myOrders = allTx.filter(tx => tx.hospital === document.getElementById("user-tag").innerText);

    if (myOrders.length === 0) return;

    let html = "<ul>";
    myOrders.forEach(tx => {
        html += `<li style="font-size: 0.85rem; padding: 8px 0; border-bottom: 1px solid #334155;">
            Ordered <strong>${tx.qty}x ${tx.item}</strong> from ${tx.seller}
        </li>`;
    });
    html += "</ul>";
    container.innerHTML = html;
}
// Call this inside loadDashboardData()!