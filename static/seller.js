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
        container.innerHTML = "<p>No transactions recorded.</p>";
        return;
    }

    let html = "<ul>";
    data.forEach(tx => {
        html += `<li style="border-bottom: 1px solid #334155; padding: 10px 0;">
            <strong style="color: #00fff5;">${tx.hospital}</strong> bought ${tx.qty}x ${tx.item} <br>
            <small style="color: #64748b;">Hash: ${tx.hash_id.substring(0,20)}...</small>
        </li>`;
    });
    html += "</ul>";
    container.innerHTML = html;
}