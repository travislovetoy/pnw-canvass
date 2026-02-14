/* ── Pin Designations ── */
const DESIGNATIONS = [
    { key: 'follow_with_signal', label: 'Follow With Signal', color: '#4CAF50', symbol: '\u2713' },
    { key: 'one_legger',         label: 'One Legger',         color: '#FF9800', symbol: '1L' },
    { key: 'mulling',            label: 'Mulling',            color: '#9C27B0', symbol: '?' },
    { key: 'inconvenient',       label: 'Inconvenient',       color: '#795548', symbol: 'IC' },
    { key: 'no_decision_maker',  label: 'No Decision Maker',  color: '#607D8B', symbol: 'ND' },
    { key: 'spanish_speaking',   label: 'Spanish Speaking',   color: '#E65100', symbol: 'ES' },
    { key: 'follow_up',          label: 'Follow Up',          color: '#2196F3', symbol: 'FU' },
    { key: 'not_home',           label: 'Not Home',           color: '#9E9E9E', symbol: 'NH' },
    { key: 'recluse',            label: 'Recluse',            color: '#424242', symbol: 'RC' },
    { key: 'abandoned_homes',    label: 'Abandoned Homes',    color: '#000000', symbol: 'AH' },
    { key: 'no_access',          label: 'No Access',          color: '#F44336', symbol: 'NA' },
    { key: 'no_nid',             label: 'No NID',             color: '#E91E63', symbol: 'NN' },
    { key: 'no_termination',     label: 'No Termination',     color: '#D32F2F', symbol: 'NT' },
    { key: 'no_signal',          label: 'No Signal',          color: '#B71C1C', symbol: 'NS' },
    { key: 'terminated_with_signal', label: 'Terminated With Signal', color: '#00BCD4', symbol: 'TS' },
    { key: 'sold_100mbps',       label: 'Sold 100Mbps',       color: '#8BC34A', symbol: '$1' },
    { key: 'sold_1gig',          label: 'Sold 1 Gig',         color: '#43A047', symbol: '$G' },
    { key: 'sold_10gig',         label: 'Sold 10 Gig',        color: '#1B5E20', symbol: '$X' },
    { key: 'no_internet',        label: 'No Internet',         color: '#FFEB3B', symbol: 'NI' },
    { key: 'gentile',            label: 'Gentile',             color: '#03A9F4', symbol: 'GN' },
    { key: 'other_isp',          label: 'Other ISP',           color: '#FF6F00', symbol: 'OI' },
    { key: 'agro_no_comms',      label: 'Agro/No Comms',       color: '#D50000', symbol: 'AG' },
    { key: 'moving',             label: 'Moving',              color: '#78909C', symbol: 'MV' },
];

const desigMap = {};
DESIGNATIONS.forEach(d => desigMap[d.key] = d);

/* ── Mapbox Token (injected from server config) ── */
mapboxgl.accessToken = MAPBOX_TOKEN;

/* ── Map Init with Mapbox Satellite ── */
// Start hidden until we get location
document.getElementById('map').style.visibility = 'hidden';

let startCenter = [-120.5, 47.23];
let startZoom = 15;

// Block on geolocation before creating map
function initMap(center, zoom) {
    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/satellite-streets-v12',
        center: center,
        zoom: zoom,
        maxZoom: 24,
    });

    map.addControl(new MapboxGeocoder({
        accessToken: MAPBOX_TOKEN,
        mapboxgl: mapboxgl,
        placeholder: 'Search address or city',
        collapsed: true,
    }), 'top-left');

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.addControl(new mapboxgl.GeolocateControl({
        positionOptions: { enableHighAccuracy: true },
        trackUserLocation: true,
        showUserHeading: true,
    }), 'top-right');

    map.on('load', () => {
        document.getElementById('map').style.visibility = 'visible';
    });

    return map;
}

// Get location first, then create map
const mapReady = new Promise((resolve) => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                resolve(initMap([pos.coords.longitude, pos.coords.latitude], 15));
            },
            () => {
                // Fallback if denied
                resolve(initMap(startCenter, 8));
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        resolve(initMap(startCenter, 8));
    }
});

// We need `map` available globally for the rest of the code
let map;
mapReady.then(m => { map = m; setupMapEvents(); });

/* ── Helper: create marker DOM element ── */
function createMarkerEl(key) {
    const d = desigMap[key] || desigMap['not_home'];
    const textColor = isLightColor(d.color) ? '#000' : '#fff';
    const fontSize = d.symbol.length > 2 ? '8px' : '10px';
    const el = document.createElement('div');
    el.style.cssText = `width:22px;height:22px;border-radius:50%;background:${d.color};border:2px solid #fff;box-shadow:0 0 4px rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;cursor:pointer;`;
    el.innerHTML = `<span style="color:${textColor};font-size:${fontSize};font-weight:700;line-height:1;">${d.symbol}</span>`;
    return el;
}

function isLightColor(hex) {
    const c = hex.replace('#', '');
    const r = parseInt(c.substr(0, 2), 16);
    const g = parseInt(c.substr(2, 2), 16);
    const b = parseInt(c.substr(4, 2), 16);
    return (r * 299 + g * 587 + b * 114) / 1000 > 160;
}

/* ── Active Designation ── */
let activeDesignation = null;

/* ── Build Bottom Pin Bar ── */
function buildPinBar() {
    const bar = document.getElementById('pin-bar');
    DESIGNATIONS.forEach(d => {
        const item = document.createElement('div');
        item.className = 'pin-item';
        item.dataset.key = d.key;

        const textColor = isLightColor(d.color) ? '#000' : '#fff';
        const fontSize = d.symbol.length > 2 ? '9px' : '11px';
        item.innerHTML = `
            <div class="pin-circle" style="background:${d.color};">
                <span style="color:${textColor};font-size:${fontSize};font-weight:700;">${d.symbol}</span>
            </div>
            <div class="pin-label">${d.label}</div>
        `;
        item.onclick = () => selectDesignation(d.key);
        bar.appendChild(item);
    });
}

function selectDesignation(key) {
    if (activeDesignation === key) {
        activeDesignation = null;
        document.querySelectorAll('.pin-item').forEach(el => el.classList.remove('active'));
    } else {
        activeDesignation = key;
        document.querySelectorAll('.pin-item').forEach(el => {
            el.classList.toggle('active', el.dataset.key === key);
        });
    }
}

/* ── Reverse Geocoding via Mapbox ── */
async function reverseGeocode(lat, lon) {
    try {
        const r = await fetch(`https://api.mapbox.com/search/geocode/v6/reverse?longitude=${lon}&latitude=${lat}&access_token=${MAPBOX_TOKEN}`);
        const data = await r.json();
        const feat = data.features && data.features[0];
        if (!feat) return { street: '', city: '', state: 'WA', zip: '', full: '' };
        const ctx = feat.properties.context || {};
        const addr = feat.properties.full_address || feat.properties.name || '';
        return {
            street: feat.properties.name_preferred || feat.properties.name || '',
            city: (ctx.place && ctx.place.name) || (ctx.locality && ctx.locality.name) || '',
            state: (ctx.region && ctx.region.region_code) || 'WA',
            zip: (ctx.postcode && ctx.postcode.name) || '',
            full: addr,
        };
    } catch (e) {
        return { street: '', city: '', state: 'WA', zip: '', full: '' };
    }
}

/* ── Track all markers for cleanup ── */
const markers = [];
/* ── Map visit ID → { marker, visit } for marker swaps ── */
const markerByVisitId = {};

/* ── setupMapEvents: called after map is created from geolocation ── */
function setupMapEvents() {

    async function loadVisits() {
        const r = await fetch('/api/visits');
        const visits = await r.json();
        markers.forEach(m => m.remove());
        markers.length = 0;
        visits.forEach(v => {
            const desig = v.designation || v.status || 'not_home';
            const el = createMarkerEl(desig);
            const marker = new mapboxgl.Marker({ element: el })
                .setLngLat([v.lon, v.lat])
                .addTo(map);
            el.addEventListener('click', (e) => {
                e.stopPropagation();
                openSidePanel(v);
            });
            markers.push(marker);
            markerByVisitId[v.id] = { marker, visit: v };
        });
    }

    async function loadTerritories() {
        const r = await fetch('/api/territories');
        const territories = await r.json();
        if (map.loaded()) {
            addTerritoryLayers(territories);
        } else {
            map.on('load', () => addTerritoryLayers(territories));
        }
    }

    function addTerritoryLayers(territories) {
        territories.forEach((t) => {
            const srcId = `territory-${t.id}`;
            if (map.getSource(srcId)) return;
            try {
                const geo = JSON.parse(t.polygon_geojson);
                map.addSource(srcId, { type: 'geojson', data: geo });
                map.addLayer({
                    id: `territory-fill-${t.id}`,
                    type: 'fill',
                    source: srcId,
                    paint: { 'fill-color': t.color, 'fill-opacity': 0.1 },
                });
                map.addLayer({
                    id: `territory-line-${t.id}`,
                    type: 'line',
                    source: srcId,
                    paint: { 'line-color': t.color, 'line-width': 2 },
                });
            } catch(e) {}
        });
    }

    /* ── Map Click: Drop Pin + Save Visit ── */
    map.on('click', async (e) => {
        if (!activeDesignation) return;

        const lat = e.lngLat.lat;
        const lon = e.lngLat.lng;

        const addr = await reverseGeocode(lat, lon);
        const addressStr = [addr.street, addr.city, addr.state, addr.zip].filter(Boolean).join(', ');

        const visitData = {
            lat: lat,
            lon: lon,
            address: addressStr,
            status: 'not_home',
            designation: activeDesignation,
        };

        const r = await fetch('/api/visits', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(visitData),
        });
        const visit = await r.json();
        visit._addr = addr;

        const el = createMarkerEl(visit.designation || activeDesignation);
        const marker = new mapboxgl.Marker({ element: el })
            .setLngLat([visit.lon, visit.lat])
            .addTo(map);
        el.addEventListener('click', (ev) => {
            ev.stopPropagation();
            openSidePanel(visit);
        });
        markers.push(marker);
        markerByVisitId[visit.id] = { marker, visit };
    });

    loadVisits();
    loadTerritories();
}

/* ── Side Panel ── */
let currentPanelVisitId = null;

function openSidePanel(visit) {
    const panel = document.getElementById('side-panel');
    panel.style.width = '320px';
    currentPanelVisitId = visit.id;

    document.getElementById('lead-lat').value = visit.lat;
    document.getElementById('lead-lon').value = visit.lon;
    document.getElementById('lead-visit-id').value = visit.id;
    document.getElementById('lead-lead-id').value = visit.lead_id || '';

    // Set designation dropdown
    setDesigSelected(visit.designation || 'not_home');
    document.getElementById('desig-options').classList.remove('open');

    if (visit._addr) {
        document.getElementById('lead-street').value = visit._addr.street;
        document.getElementById('lead-city').value = visit._addr.city;
        document.getElementById('lead-state').value = visit._addr.state || 'WA';
        document.getElementById('lead-zip').value = visit._addr.zip;
    } else {
        const parts = (visit.address || '').split(',').map(s => s.trim());
        document.getElementById('lead-street').value = parts[0] || '';
        document.getElementById('lead-city').value = parts[1] || '';
        document.getElementById('lead-state').value = parts[2] || 'WA';
        document.getElementById('lead-zip').value = parts[3] || '';
    }

    // Populate lead data if this visit has a linked lead
    document.getElementById('lead-first').value = visit.lead_first || '';
    document.getElementById('lead-last').value = visit.lead_last || '';
    document.getElementById('lead-email').value = visit.lead_email || '';
    document.getElementById('lead-phone').value = visit.lead_phone || '';
    document.getElementById('lead-notes').value = visit.lead_notes || '';

    // Set service plan dropdown to matching plan
    const svcTier = visit.lead_service_tier || '';
    document.getElementById('lead-service-plan').value = svcTier;

    document.getElementById('lead-save-status').textContent = visit.lead_first ? '' : '';

    setTimeout(() => map.resize(), 250);
}

function closeSidePanel() {
    document.getElementById('side-panel').style.width = '0';
    setTimeout(() => map.resize(), 250);
}

document.getElementById('btn-close-panel').onclick = closeSidePanel;

/* ── Delete Pin ── */
document.getElementById('btn-delete-visit').onclick = async () => {
    const visitId = currentPanelVisitId;
    if (!visitId) return;
    if (!confirm('Delete this pin?')) return;

    await fetch(`/api/visits/${visitId}`, { method: 'DELETE' });

    // Remove marker from map
    const entry = markerByVisitId[visitId];
    if (entry) {
        entry.marker.remove();
        delete markerByVisitId[visitId];
    }

    closeSidePanel();
};

/* ── Load UISP Service Plans ── */
(async function loadServicePlans() {
    try {
        const r = await fetch('/api/service-plans');
        const plans = await r.json();
        const sel = document.getElementById('lead-service-plan');
        plans.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            let label = p.name;
            if (p.price !== null) label += ` — $${p.price}/mo`;
            if (p.downloadSpeed) label += ` (${p.downloadSpeed >= 1000 ? (p.downloadSpeed / 1000) + 'G' : p.downloadSpeed + 'Mbps'})`;
            opt.textContent = label;
            sel.appendChild(opt);
        });
    } catch (e) {}
})();

/* ── Custom Designation Dropdown ── */
function desigDotHTML(d) {
    const tc = isLightColor(d.color) ? '#000' : '#fff';
    return `<span class="desig-dot" style="background:${d.color};"><span style="color:${tc};">${d.symbol}</span></span>`;
}

function setDesigSelected(key) {
    const d = desigMap[key] || desigMap['not_home'];
    const selEl = document.getElementById('desig-selected');
    const tc = isLightColor(d.color) ? '#000' : '#fff';
    selEl.style.backgroundColor = d.color;
    selEl.style.color = tc;
    selEl.innerHTML = `${desigDotHTML(d)} ${d.label}`;
    document.getElementById('lead-designation').value = key;
}

(function buildDesigDropdown() {
    const opts = document.getElementById('desig-options');
    DESIGNATIONS.forEach(d => {
        const row = document.createElement('div');
        row.className = 'desig-option';
        row.dataset.key = d.key;
        const tc = isLightColor(d.color) ? '#000' : '#fff';
        row.style.backgroundColor = d.color;
        row.style.color = tc;
        row.innerHTML = `${desigDotHTML(d)} ${d.label}`;
        row.addEventListener('click', () => selectDesig(d.key));
        opts.appendChild(row);
    });

    document.getElementById('desig-selected').addEventListener('click', () => {
        opts.classList.toggle('open');
    });

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!document.getElementById('desig-dropdown').contains(e.target)) {
            opts.classList.remove('open');
        }
    });
})();

async function selectDesig(key) {
    document.getElementById('desig-options').classList.remove('open');
    setDesigSelected(key);

    const visitId = currentPanelVisitId;
    if (!visitId) return;

    await fetch(`/api/visits/${visitId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ designation: key }),
    });

    // Swap the marker on the map
    const entry = markerByVisitId[visitId];
    if (entry) {
        const lngLat = entry.marker.getLngLat();
        entry.marker.remove();
        const el = createMarkerEl(key);
        const newMarker = new mapboxgl.Marker({ element: el })
            .setLngLat(lngLat)
            .addTo(map);
        entry.visit.designation = key;
        el.addEventListener('click', (ev) => {
            ev.stopPropagation();
            openSidePanel(entry.visit);
        });
        entry.marker = newMarker;
    }
}

/* ── Init ── */
buildPinBar();
