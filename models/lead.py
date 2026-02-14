from models.db import get_db

VALID_STAGES = ("new_lead", "contacted", "quoted", "won", "lost")


def get_all_leads(filters=None):
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if filters:
        if filters.get("pipeline_stage"):
            query += " AND pipeline_stage = ?"
            params.append(filters["pipeline_stage"])
        if filters.get("rep_id"):
            query += " AND created_by_rep_id = ?"
            params.append(filters["rep_id"])
        if filters.get("territory_id"):
            query += " AND territory_id = ?"
            params.append(filters["territory_id"])
    query += " ORDER BY created_at DESC"
    return get_db().execute(query, params).fetchall()


def get_lead_by_id(lead_id):
    return get_db().execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()


def create_lead(data):
    db = get_db()
    row = db.execute(
        """INSERT INTO leads
        (first_name, last_name, street1, city, state, zip, lat, lon, phone, email,
         service_tags, pipeline_stage, notes, organization_id, created_by_rep_id, territory_id,
         service_type, service_tier)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id""",
        (
            data["first_name"], data["last_name"],
            data.get("street1", ""), data.get("city", ""), data.get("state", "WA"),
            data.get("zip", ""), data.get("lat"), data.get("lon"),
            data.get("phone", ""), data.get("email", ""),
            data.get("service_tags", ""), data.get("pipeline_stage", "new_lead"),
            data.get("notes", ""), data.get("organization_id", 1),
            data.get("created_by_rep_id"), data.get("territory_id"),
            data.get("service_type", ""), data.get("service_tier", ""),
        ),
    ).fetchone()
    db.commit()
    return row[0]


def update_lead(lead_id, data):
    db = get_db()
    fields = []
    params = []
    for key in ("first_name", "last_name", "street1", "city", "state", "zip",
                "lat", "lon", "phone", "email", "service_tags", "pipeline_stage",
                "notes", "organization_id", "territory_id",
                "service_type", "service_tier"):
        if key in data:
            fields.append(f"{key} = ?")
            params.append(data[key])
    if not fields:
        return
    params.append(lead_id)
    db.execute(f"UPDATE leads SET {', '.join(fields)} WHERE id = ?", params)
    db.commit()


def update_lead_stage(lead_id, stage):
    if stage not in VALID_STAGES:
        raise ValueError(f"Invalid stage: {stage}")
    db = get_db()
    db.execute("UPDATE leads SET pipeline_stage = ? WHERE id = ?", (stage, lead_id))
    db.commit()


def mark_uisp_synced(lead_id, uisp_client_id):
    db = get_db()
    db.execute(
        "UPDATE leads SET uisp_synced = 1, uisp_client_id = ? WHERE id = ?",
        (uisp_client_id, lead_id),
    )
    db.commit()


def mark_uisp_failed(lead_id):
    db = get_db()
    db.execute("UPDATE leads SET uisp_synced = -1 WHERE id = ?", (lead_id,))
    db.commit()


def delete_lead(lead_id):
    db = get_db()
    db.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    db.commit()
