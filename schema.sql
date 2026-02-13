CREATE TABLE IF NOT EXISTS reps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS territories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    polygon_geojson TEXT NOT NULL,
    assigned_rep_id INTEGER,
    color TEXT NOT NULL DEFAULT '#3388ff',
    FOREIGN KEY (assigned_rep_id) REFERENCES reps(id)
);

CREATE TABLE IF NOT EXISTS territory_reps (
    territory_id INTEGER NOT NULL,
    rep_id INTEGER NOT NULL,
    PRIMARY KEY (territory_id, rep_id),
    FOREIGN KEY (territory_id) REFERENCES territories(id),
    FOREIGN KEY (rep_id) REFERENCES reps(id)
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    street1 TEXT,
    city TEXT,
    state TEXT DEFAULT 'WA',
    zip TEXT,
    lat REAL,
    lon REAL,
    phone TEXT,
    email TEXT,
    service_tags TEXT DEFAULT '',
    pipeline_stage TEXT NOT NULL DEFAULT 'new_lead',
    notes TEXT DEFAULT '',
    organization_id INTEGER DEFAULT 1,
    uisp_client_id INTEGER,
    uisp_synced INTEGER NOT NULL DEFAULT 0,
    created_by_rep_id INTEGER,
    territory_id INTEGER,
    service_type TEXT DEFAULT '',
    service_tier TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_rep_id) REFERENCES reps(id),
    FOREIGN KEY (territory_id) REFERENCES territories(id)
);

CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'not_home',
    designation TEXT DEFAULT 'not_home',
    notes TEXT DEFAULT '',
    lead_id INTEGER,
    rep_id INTEGER,
    territory_id INTEGER,
    visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (rep_id) REFERENCES reps(id),
    FOREIGN KEY (territory_id) REFERENCES territories(id)
);
