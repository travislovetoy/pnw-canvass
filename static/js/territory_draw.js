mapboxgl.accessToken = MAPBOX_TOKEN;

const tMap = new mapboxgl.Map({
    container: 'territory-map',
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [-120.5, 47.23],
    zoom: 8,
});

tMap.addControl(new mapboxgl.NavigationControl(), 'bottom-right');

tMap.addControl(new MapboxGeocoder({
    accessToken: MAPBOX_TOKEN,
    mapboxgl: mapboxgl,
    placeholder: 'Search address or city',
    collapsed: true,
}), 'top-right');

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

let allReps = [];

async function loadRepsCheckboxes() {
    try {
        const r = await fetch('/api/reps');
        allReps = await r.json();
        renderFormCheckboxes([]);
    } catch(e) {}
}

function renderFormCheckboxes(selectedIds) {
    const container = document.getElementById('t-reps-checklist');
    if (!container) return;
    container.innerHTML = '';
    allReps.forEach(rep => {
        const checked = selectedIds.includes(rep.id) ? 'checked' : '';
        container.innerHTML += `
            <div class="form-check">
                <input class="form-check-input t-rep-cb" type="checkbox" value="${rep.id}" id="t-rep-${rep.id}" ${checked}>
                <label class="form-check-label small" for="t-rep-${rep.id}">${rep.full_name}</label>
            </div>`;
    });
}

function getCheckedRepIds() {
    return Array.from(document.querySelectorAll('.t-rep-cb:checked')).map(cb => parseInt(cb.value));
}

function renderCardCheckboxes(tid, selectedIds) {
    let html = '';
    allReps.forEach(rep => {
        const checked = selectedIds.includes(rep.id) ? 'checked' : '';
        html += `
            <div class="form-check">
                <input class="form-check-input card-rep-cb" type="checkbox" value="${rep.id}" data-tid="${tid}" ${checked}>
                <label class="form-check-label small">${rep.full_name}</label>
            </div>`;
    });
    html += `<button class="btn btn-primary btn-sm mt-1 btn-save-card-reps" data-tid="${tid}">Save</button>`;
    return html;
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
    const isAdmin = !!document.getElementById('territory-form');

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

        const repDisplay = t.rep_names || 'Unassigned';
        const repIds = t.rep_ids || [];

        const div = document.createElement('div');
        div.className = 'card card-body p-2 mb-2';
        let cardHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <span style="display:inline-block;width:12px;height:12px;border-radius:2px;background:${t.color};margin-right:4px"></span>
                    <strong>${t.name}</strong>
                    <br><small class="text-muted">${repDisplay}</small>
                </div>
                <div>`;
        if (isAdmin) {
            cardHTML += `<button class="btn btn-outline-primary btn-sm me-1 btn-assign-reps" data-tid="${t.id}" data-reps='${JSON.stringify(repIds)}'>Reps</button>`;
            cardHTML += `<button class="btn btn-outline-danger btn-sm" onclick="deleteTerritory(${t.id})">Del</button>`;
        }
        cardHTML += `</div></div>`;
        if (isAdmin) {
            cardHTML += `<div class="assign-reps-panel mt-2" id="assign-panel-${t.id}" style="display:none;"></div>`;
        }
        div.innerHTML = cardHTML;
        listEl.appendChild(div);
    });

    // Bind assign reps buttons
    document.querySelectorAll('.btn-assign-reps').forEach(btn => {
        btn.addEventListener('click', () => {
            const tid = parseInt(btn.dataset.tid);
            const repIds = JSON.parse(btn.dataset.reps);
            const panel = document.getElementById('assign-panel-' + tid);
            if (panel.style.display === 'none') {
                panel.style.display = 'block';
                panel.innerHTML = renderCardCheckboxes(tid, repIds);
                panel.querySelector('.btn-save-card-reps').addEventListener('click', async () => {
                    const checked = Array.from(panel.querySelectorAll('.card-rep-cb:checked')).map(cb => parseInt(cb.value));
                    await fetch(`/api/territories/${tid}/reps`, {
                        method: 'PUT',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ rep_ids: checked }),
                    });
                    loadTerritories();
                });
            } else {
                panel.style.display = 'none';
            }
        });
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
        const repIds = getCheckedRepIds();
        const body = {
            name: name,
            polygon_geojson: geojson,
            color: document.getElementById('t-color').value,
            rep_ids: repIds,
        };

        if (editId) {
            await fetch(`/api/territories/${editId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body),
            });
            await fetch(`/api/territories/${editId}/reps`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ rep_ids: repIds }),
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
        renderFormCheckboxes([]);
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
loadRepsCheckboxes();
