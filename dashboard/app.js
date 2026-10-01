async function load() {
  try {
    const h = await fetch("/health").then(r => r.json());
    document.getElementById("health").textContent = h.status.toUpperCase();
  } catch (err) {
    document.getElementById("health").textContent = "ERROR";
  }
  await loadIncidents();
}
async function loadIncidents() {
  try {
    const data = await fetch("/api/v1/incidents").then(r => r.json());
    document.getElementById("count").textContent = data.length;
    document.getElementById("incidents").textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    document.getElementById("count").textContent = "ERROR";
    document.getElementById("incidents").textContent = "Error loading incidents";
  }
}
load();
setInterval(load, 30000);
