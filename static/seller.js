document.addEventListener("DOMContentLoaded", () => {
    fetchLedger();
    
    document.getElementById("add-form").addEventListener("submit", async (e) => {
        e.preventDefault();
        const item = document.getElementById("item").value;
        const qty = parseInt(document.getElementById("qty").value);

        const res = await fetch("/api/add-inventory", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ item, qty })
        });

        if (res.ok) {
            alert("Inventory Updated!");
            location.reload();
        }
    });
});

async function fetchLedger() {
    const res = await fetch("/ledger");
    const data = await res.json();
    const container = document.getElementById("ledger-box");
    
    if (data.length === 0) {
        container.innerHTML = "<p style='color: #64748b;'>No orders received yet.</p>";
        return;
    }

    let html = "<ul style='list-style: none; padding: 0;'>";
    data.forEach(tx => {
        html += `
        <li style="border-bottom: 1px solid #334155; padding: 15px 0; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong style="color: #00fff5; font-size: 1.1rem;">${tx.hospital.replace(/_/g, ' ').toUpperCase()}</strong><br>
                <span style="color: #e2e8f0;">Ordered: ${tx.qty}x ${tx.item}</span><br>
                <small style="color: #64748b; font-family: monospace;">ID: ${tx.hash_id.substring(0,12)}...</small>
            </div>
            <div>
                <a href="/track/${tx.hash_id}" 
                   style="background: #fbbf24; color: #000; padding: 5px 12px; border-radius: 5px; text-decoration: none; font-weight: bold; font-size: 0.8rem;">
                   TRACK & DISPATCH
                </a>
            </div>
        </li>`;
    });
    html += "</ul>";
    container.innerHTML = html;
}