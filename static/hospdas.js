async function loadAll() {
  const profile = await fetch("/api/hospital/profile").then(r=>r.json());
  document.getElementById("hospital-name").value = profile.display_name;
  document.getElementById("my-inventory").innerText =
    JSON.stringify(profile.inventory, null, 2);

  const others = await fetch("/api/hospitals/others").then(r=>r.json());
  document.getElementById("other-hospitals").innerHTML =
    others.map(h=>`<pre>${h.name}: ${JSON.stringify(h.inventory)}</pre>`).join("");

  const sellers = await fetch("/api/sellers").then(r=>r.json());
  document.getElementById("supplier-list").innerHTML =
    sellers.map(s=>`<p>${s.seller_name} - ${s.item}: ${s.qty}</p>`).join("");
}

async function saveProfile() {
  const inventory = JSON.parse(prompt("Enter inventory JSON"));
  await fetch("/api/hospital/profile", {
    method:"POST",
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      display_name: document.getElementById("hospital-name").value,
      inventory
    })
  });
  loadAll();
}

loadAll();
