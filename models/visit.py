from models.db import get_db

VALID_STATUSES = ("not_home", "not_interested", "interested", "signed_up")

VALID_DESIGNATIONS = (
    "follow_with_signal", "one_legger", "mulling", "inconvenient",
    "no_decision_maker", "spanish_speaking", "follow_up", "not_home",
    "recluse", "abandoned_homes", "no_access", "no_nid", "no_termination",
    "no_signal", "terminated_with_signal", "sold_100mbps", "sold_1gig",
    "sold_10gig", "no_internet", "gentile", "other_isp", "agro_no_comms",
    "moving",
)


def get_all_visits(filters=None):
    query = """SELECT v.*, r.full_name AS rep_name,
        l.first_name AS lead_first, l.last_name AS lead_last,
        l.phone AS lead_phone, l.email AS lead_email,
        l.notes AS lead_notes, l.service_type AS lead_service_type,
        l.service_tier AS lead_service_tier, l.id AS lead_id_ref
        FROM visits v
        LEFT JOIN reps r ON v.rep_id = r.id
        LEFT JOIN leads l ON v.lead_id = l.id
        WHERE 1=1"""
    params = []
    if filters:
        if filters.get("rep_id"):
            query += " AND v.rep_id = ?"
            params.append(filters["rep_id"])
        if filters.get("status"):
            query += " AND v.status = ?"
            params.append(filters["status"])
        if filters.get("designation"):
            query += " AND v.designation = ?"
            params.append(filters["designation"])
        if filters.get("territory_id"):
            query += " AND v.territory_id = ?"
            params.append(filters["territory_id"])
        if filters.get("date_from"):
            query += " AND v.visited_at >= ?"
            params.append(filters["date_from"])
        if filters.get("date_to"):
            query += " AND v.visited_at <= ?"
            params.append(filters["date_to"] + " 23:59:59")
    query += " ORDER BY v.visited_at DESC"
    return get_db().execute(query, params).fetchall()


def get_visit_by_id(visit_id):
    return get_db().execute("SELECT * FROM visits WHERE id = ?", (visit_id,)).fetchone()


def create_visit(data):
    db = get_db()
    row = db.execute(
        """INSERT INTO visits (lat, lon, address, status, designation, notes, lead_id, rep_id, territory_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING id""",
        (
            data["lat"], data["lon"], data.get("address", ""),
            data.get("status", "not_home"), data.get("designation", "not_home"),
            data.get("notes", ""),
            data.get("lead_id"), data.get("rep_id"), data.get("territory_id"),
        ),
    ).fetchone()
    db.commit()
    return row[0]


def update_visit(visit_id, data):
    db = get_db()
    fields = []
    params = []
    for key in ("status", "designation", "notes", "lead_id", "address"):
        if key in data:
            fields.append(f"{key} = ?")
            params.append(data[key])
    if not fields:
        return
    params.append(visit_id)
    db.execute(f"UPDATE visits SET {', '.join(fields)} WHERE id = ?", params)
    db.commit()


def delete_visit(visit_id):
    db = get_db()
    db.execute("DELETE FROM visits WHERE id = ?", (visit_id,))
    db.commit()
