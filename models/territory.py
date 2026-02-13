from models.db import get_db


def get_all_territories():
    return get_db().execute(
        "SELECT t.id, t.name, t.polygon_geojson, t.assigned_rep_id, t.color, "
        "GROUP_CONCAT(r.full_name) AS rep_names, "
        "GROUP_CONCAT(r.id) AS rep_ids "
        "FROM territories t "
        "LEFT JOIN territory_reps tr ON t.id = tr.territory_id "
        "LEFT JOIN reps r ON tr.rep_id = r.id "
        "GROUP BY t.id ORDER BY t.id"
    ).fetchall()


def get_territory_by_id(tid):
    return get_db().execute("SELECT * FROM territories WHERE id = ?", (tid,)).fetchone()


def get_territory_reps(tid):
    return get_db().execute(
        "SELECT r.id, r.full_name FROM reps r "
        "JOIN territory_reps tr ON r.id = tr.rep_id "
        "WHERE tr.territory_id = ?", (tid,)
    ).fetchall()


def assign_reps_to_territory(tid, rep_ids):
    db = get_db()
    db.execute("DELETE FROM territory_reps WHERE territory_id = ?", (tid,))
    for rid in rep_ids:
        db.execute(
            "INSERT INTO territory_reps (territory_id, rep_id) VALUES (?, ?)",
            (tid, rid),
        )
    db.commit()


def create_territory(name, polygon_geojson, assigned_rep_id=None, color="#3388ff"):
    db = get_db()
    db.execute(
        "INSERT INTO territories (name, polygon_geojson, assigned_rep_id, color) VALUES (?, ?, ?, ?)",
        (name, polygon_geojson, assigned_rep_id, color),
    )
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def update_territory(tid, name, polygon_geojson, assigned_rep_id, color):
    db = get_db()
    db.execute(
        "UPDATE territories SET name=?, polygon_geojson=?, assigned_rep_id=?, color=? WHERE id=?",
        (name, polygon_geojson, assigned_rep_id, color, tid),
    )
    db.commit()


def delete_territory(tid):
    db = get_db()
    db.execute("DELETE FROM territory_reps WHERE territory_id = ?", (tid,))
    db.execute("DELETE FROM territories WHERE id = ?", (tid,))
    db.commit()
