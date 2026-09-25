async function load() {
  const h = await fetch("/health").then(r => r.json());
  document.getElementById("health").textContent = h.status.toUpperCase();
  await loadIncidents();
}
async function loadIncidents() {
  const data = await fetch("/api/v1/incidents").then(r => r.json());
  document.getElementById("count").textContent = data.length;
  document.getElementById("incidents").textContent = JSON.stringify(data, null, 2);
}
load();
