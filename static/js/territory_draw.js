mapboxgl.accessToken = MAPBOX_TOKEN;

const tMap = new mapboxgl.Map({
    container: 'territory-map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-120.5, 47.23],
    zoom: 8,
});

tMap.addControl(new mapboxgl.NavigationControl(), 'top-right');

// Geolocate on load (same pattern as main map)
if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
        pos => {
            tMap.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 15 });
        },
        () => {},
        { enableHighAccuracy: true, timeout: 5000 }
    );
}

// Drawing controls (admin only — draw control exists only if form is present)
let draw = null;
if (document.getElementById('territory-form')) {
    draw = new MapboxDraw({
        displayControlsDefault: false,
        controls: { polygon: true, trash: true },
    });
    tMap.addControl(draw, 'top-left');

    tMap.on('draw.create', updateGeoJSON);
    tMap.on('draw.update', updateGeoJSON);
    tMap.on('draw.delete', () => {
        document.getElementById('t-geojson').value = '';
    });
}

function updateGeoJSON() {
    const data = draw.getAll();
    if (data.features.length > 0) {
        // Keep only the last drawn polygon
        const lastFeature = data.features[data.features.length - 1];
        // Remove all other features
        data.features.forEach(f => {
            if (f.id !== lastFeature.id) draw.delete(f.id);
        });
        document.getElementById('t-geojson').value = JSON.stringify(lastFeature.geometry);
    } else {
        document.getElementById('t-geojson').value = '';
    }
}

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

let territorySourceIds = [];

async function loadTerritories() {
    const r = await fetch('/api/territories');
    const territories = await r.json();

    // Remove old territory layers/sources
    territorySourceIds.forEach(id => {
        if (tMap.getLayer(id + '-fill')) tMap.removeLayer(id + '-fill');
        if (tMap.getLayer(id + '-line')) tMap.removeLayer(id + '-line');
        if (tMap.getSource(id)) tMap.removeSource(id);
    });
    territorySourceIds = [];

    const listEl = document.getElementById('territory-list');
    listEl.innerHTML = '';

    territories.forEach(t => {
        try {
            const geo = JSON.parse(t.polygon_geojson);
            const sourceId = 'territory-' + t.id;
            territorySourceIds.push(sourceId);

            tMap.addSource(sourceId, {
                type: 'geojson',
                data: { type: 'Feature', geometry: geo },
            });
            tMap.addLayer({
                id: sourceId + '-fill',
                type: 'fill',
                source: sourceId,
                paint: { 'fill-color': t.color, 'fill-opacity': 0.15 },
            });
            tMap.addLayer({
                id: sourceId + '-line',
                type: 'line',
                source: sourceId,
                paint: { 'line-color': t.color, 'line-width': 2 },
            });
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
        if (draw) draw.deleteAll();
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
        if (draw) draw.deleteAll();
    };
}

async function deleteTerritory(id) {
    if (!confirm('Delete this territory?')) return;
    await fetch(`/api/territories/${id}`, {method: 'DELETE'});
    loadTerritories();
}

// Wait for map style to load before adding territory layers
tMap.on('load', () => {
    loadTerritories();
});
loadRepsDropdown();
