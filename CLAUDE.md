# PNW Canvass

## Project Overview
Flask-based field canvassing application for door-to-door sales teams. Tracks visits on a Mapbox satellite map with 23 pin designations, manages leads with a customer info side panel, and syncs to UISP CRM.

## Tech Stack
- **Backend:** Python 3.9 / Flask, SQLite
- **Frontend:** Mapbox GL JS v3, Bootstrap 5.3.2, vanilla JS
- **Integrations:** UISP CRM API, Mapbox Geocoding API v6
- **Other pages use:** Leaflet + Leaflet Draw (territories, etc.)

## Running the App
```bash
python3 app.py  # runs on port 5050, debug mode
```

## Environment Variables (.env)
```
MAPBOX_TOKEN=<mapbox access token>
UISP_API_TOKEN=<uisp api token>
UISP_BASE_URL=https://uispdev.pnw.net/crm/api/v1.0
DB_PATH=canvass.db
SECRET_KEY=<session secret>
```
Config uses `python-dotenv` to load `.env` automatically.

## Database
- SQLite at `canvass.db`
- Schema: `schema.sql`
- Init: `python3 init_db.py` (seeds admin/admin user)
- Migration: `python3 migrate_db.py` (adds designation, service_type, service_tier columns)

## Key Architecture

### Map Flow
1. Map opens at user's GPS location (zoom 15) using browser geolocation
2. User selects pin designation from bottom scrollbar (23 types)
3. Click map → pin drops, Mapbox reverse geocodes the address, visit saves to DB
4. Click dropped pin → side panel opens with auto-filled address
5. Fill customer info + service type → Save creates lead → UISP push

### Files
- `app.py` — Flask app factory, blueprint registration
- `config.py` — Environment-based config with dotenv
- `models/` — SQLite data layer (visit, lead, rep, territory)
- `routes/` — API endpoints and HTML views
- `services/uisp_client.py` — UISP CRM integration
- `templates/map.html` — Map page with Mapbox GL JS, pin bar, side panel
- `static/js/map.js` — Map logic, designations, geocoding, pin dropping
- `static/js/lead_form.js` — Side panel lead form save logic
- `static/css/app.css` — Pin bar styling, side panel

### Pin Designations (23 types)
Each has a unique color and 1-2 char symbol. Stored in `visits.designation` column. Defined in `map.js` DESIGNATIONS array and `models/visit.py` VALID_DESIGNATIONS tuple.

### Service Selection
- Radio: Fiber / Wireless
- Fiber shows tier dropdown: 100Mbps / 1 Gig / 10 Gig
- Wireless hides tier, sets value to "wireless"
- Stored in `leads.service_type` and `leads.service_tier`

## Login
Default admin credentials: `admin` / `admin`

## Notes
- Mapbox token is injected server-side via `{{ mapbox_token }}` template variable
- JS files use cache-busting query strings (`?v=random`)
- Leaflet is still loaded in base.html for territory drawing page
- UISP sync silently skips when no API token is configured
