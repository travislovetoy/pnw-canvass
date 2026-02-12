const tMap = L.map('territory-map').setView([47.23, -120.5], 8);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
}).addTo(tMap);

const drawnItems = new L.FeatureGroup();
tMap.addLayer(drawnItems);
const territoryDisplay = L.layerGroup().addTo(tMap);

const drawControl = new L.Control.Draw({
    edit: { featureGroup: drawnItems },
    draw: {
        polygon: true,
        polyline: false,
        rectangle: true,
        circle: false,
        marker: false,
        circlemarker: false,
    },
});
tMap.addControl(drawControl);

tMap.on(L.Draw.Event.CREATED, function(e) {
    drawnItems.clearLayers();
    drawnItems.addLayer(e.layer);
    const geo = e.layer.toGeoJSON();
    document.getElementById('t-geojson').value = JSON.stringify(geo.geometry);
});

async function loadRepsDropdown() {
    try {
        const r = await fetch('/api/reps');
        const reps = await r.json();
        const sel = document.getElementById('t-rep');
        if (!sel) return;
        reps.forEach(rep => {
            const opt = document.createElement('option');
            opt.value = rep.id;
            opt.textContent = rep.full_name;
            sel.appendChild(opt);
        });
    } catch(e) {}
}

async function loadTerritories() {
    const r = await fetch('/api/territories');
    const territories = await r.json();
    territoryDisplay.clearLayers();
    const listEl = document.getElementById('territory-list');
    listEl.innerHTML = '';

    territories.forEach(t => {
        try {
            const geo = JSON.parse(t.polygon_geojson);
            const geoFull = {type: 'Feature', geometry: geo};
            const layer = L.geoJSON(geoFull, {
                style: { color: t.color, fillOpacity: 0.15, weight: 2 },
            });
            layer.bindTooltip(t.name);
            territoryDisplay.addLayer(layer);
        } catch(e) {}

        const div = document.createElement('div');
        div.className = 'card card-body p-2 mb-2';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:${t.color};margin-right:4px"></span>
                    <strong>${t.name}</strong>
                    <br><small class="text-muted">${t.rep_name || 'Unassigned'}</small>
                </div>
                <div>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteTerritory(${t.id})">Del</button>
                </div>
            </div>`;
        listEl.appendChild(div);
    });
}

const saveTerritoryBtn = document.getElementById('btn-save-territory');
if (saveTerritoryBtn) {
    saveTerritoryBtn.onclick = async () => {
        const name = document.getElementById('t-name').value.trim();
        const geojson = document.getElementById('t-geojson').value;
        if (!name) { alert('Name required'); return; }
        if (!geojson) { alert('Draw a polygon first'); return; }

        const editId = document.getElementById('t-edit-id').value;
        const body = {
            name: name,
            polygon_geojson: geojson,
            assigned_rep_id: document.getElementById('t-rep').value || null,
            color: document.getElementById('t-color').value,
        };

        if (editId) {
            await fetch(`/api/territories/${editId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body),
            });
        } else {
            await fetch('/api/territories', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body),
            });
        }

        document.getElementById('btn-clear-territory').click();
        drawnItems.clearLayers();
        loadTerritories();
    };
}

const clearTerritoryBtn = document.getElementById('btn-clear-territory');
if (clearTerritoryBtn) {
    clearTerritoryBtn.onclick = () => {
        document.getElementById('t-name').value = '';
        document.getElementById('t-geojson').value = '';
        document.getElementById('t-edit-id').value = '';
        document.getElementById('t-color').value = '#3388ff';
        document.getElementById('t-rep').value = '';
        drawnItems.clearLayers();
    };
}

async function deleteTerritory(id) {
    if (!confirm('Delete this territory?')) return;
    await fetch(`/api/territories/${id}`, {method: 'DELETE'});
    loadTerritories();
}

loadRepsDropdown();
loadTerritories();
