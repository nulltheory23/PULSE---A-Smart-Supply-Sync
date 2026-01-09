document.addEventListener("DOMContentLoaded", () => {
    loadDashboardData();
});

async function loadDashboardData() {
    try {
        // Run all three: Profile, Marketplace, and the Ledger (My Orders)
        await Promise.all([
            fetchMyProfile(),
            fetchMarketplace(),
            fetchMyOrders()
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
        
        // 1. Update Header & Titles
        const userTag = document.getElementById("user-tag");
        const hospTitle = document.getElementById("hosp-title");
        
        if (userTag) userTag.innerText = data.display_name || "User";
        if (hospTitle) hospTitle.innerText = `${data.display_name || "Hospital"} Portal`;

        // 2. Update Inventory List with Health Badges
        const container = document.getElementById("my-stock");
        if (!container) return;

        if (!data.inventory || Object.keys(data.inventory).length === 0) {
            container.innerHTML = "<p style='color: #64748b;'>No local stock recorded.</p>";
            return;
        }

        let html = "<ul style='list-style: none; padding: 0;'>";
        for (const [item, qty] of Object.entries(data.inventory)) {
            
            // --- STOCK HEALTH LOGIC ---
            let statusColor = "#00fff5"; // Default Cyan (Safe)
            let statusText = "SAFE";
            let glowEffect = "";

            if (qty <= 5) {
                statusColor = "#ef4444"; // Red (Critical)
                statusText = "CRITICAL";
                glowEffect = "box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);";
            } else if (qty <= 15) {
                statusColor = "#fbbf24"; // Yellow (Low)
                statusText = "LOW";
            }

            html += `
                <li style="padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; ${glowEffect} border-radius: 8px; margin-bottom: 5px;">
                    <span style="font-weight: 500;">${item}: <strong style="color: ${statusColor}; font-size: 1.1rem;">${qty}</strong></span>
                    <span style="font-size: 0.65rem; color: ${statusColor}; border: 1px solid ${statusColor}; padding: 2px 8px; border-radius: 12px; font-weight: bold; letter-spacing: 0.5px;">
                        ${statusText}
                    </span>
                </li>`;
        }
        html += "</ul>";
        container.innerHTML = html;

    } catch (err) {
        console.error("Profile Error:", err);
        const container = document.getElementById("my-stock");
        if (container) container.innerHTML = "<p style='color: #ef4444;'>Error loading stock profile.</p>";
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
            container.innerHTML = "<p style='text-align: center; color: #94a3b8;'>No supplies available.</p>";
            return;
        }

        items.forEach(i => {
            const card = document.createElement("div");
            card.className = "hospital-card";
            card.style.marginBottom = "15px";
            
            // Format Supplier name for the UI
            const supplierDisplay = i.seller_name.replace(/_/g, ' ').toUpperCase();

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <div style="flex: 1;">
                        <h2 style="color: #fbbf24; margin: 0;">${i.item}</h2>
                        <p style="margin: 5px 0; font-size: 0.85rem; color: #94a3b8;">Supplier: ${supplierDisplay}</p>
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
            loadDashboardData(); // Refresh all panels
        } else {
            alert("❌ Order Failed: Stock unavailable.");
        }
    } catch (err) {
        console.error("Purchase Error:", err);
    }
}

async function fetchMyOrders() {
    try {
        const res = await fetch("/ledger");
        const myOrders = await res.json(); // Backend already filtered for current user
        const container = document.getElementById("my-orders");
        
        if (!container) return;

        if (myOrders.length === 0) {
            container.innerHTML = "<p style='color: #64748b; font-size: 0.85rem;'>No recent orders.</p>";
            return;
        }

        let html = "<ul style='list-style: none; padding: 0;'>";
        myOrders.forEach(tx => {
            const cleanSeller = tx.seller.replace(/_/g, ' ').toUpperCase();
            
            html += `
            <li style="font-size: 0.85rem; padding: 12px 0; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #94a3b8;">Ordered:</span> <strong>${tx.qty}x ${tx.item}</strong><br>
                    <small style="color: #64748b;">From: ${cleanSeller}</small>
                </div>
                <a href="/track/${tx.hash_id}" 
                   style="color: #00fff5; text-decoration: none; border: 1px solid #00fff5; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem;">
                   Track
                </a>
            </li>`;
        });
        html += "</ul>";
        container.innerHTML = html;
    } catch (err) {
        console.error("Order Fetch Error:", err);
    }
}