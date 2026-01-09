document.addEventListener("DOMContentLoaded", () => {
    fetchLedger();

    const invForm = document.getElementById("inventory-form");
    invForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const item = document.getElementById("item-name").value;
        const qty = parseInt(document.getElementById("item-qty").value);

        try {
            const response = await fetch("/api/add-inventory", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ item: item, qty: qty })
            });

            const result = await response.json();

            if (result.success) {
                alert(`✅ Success: ${result.message}`);
                invForm.reset();
                fetchLedger(); 
            } else {
                alert("❌ Error updating inventory.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Connection failed!");
        }
    });
});

function fetchLedger() {
    fetch("/ledger")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("ledger-container");
            if (!data || data.length === 0) {
                container.innerHTML = "<p style='color: #94a3b8; text-align: center;'>No transactions found yet.</p>";
                return;
            }

            let html = "<ul style='list-style: none; padding: 0;'>";
            data.forEach(tx => {
                html += `
                    <li style="border-bottom: 1px solid rgba(255,255,255,0.1); padding: 15px 0;">
                        <span style="color: #00fff5; font-weight: bold;">${tx.hospital}</span> requested 
                        <strong>${tx.qty}x ${tx.item}</strong><br>
                        <small style="color: #64748b; font-family: monospace;">HASH: ${tx.hash_id.substring(0, 24)}...</small>
                    </li>
                `;
            });
            html += "</ul>";
            container.innerHTML = html;
        })
        .catch(err => {
            console.error("Ledger Error:", err);
            document.getElementById("ledger-container").innerHTML = "Error loading ledger.";
        });
}