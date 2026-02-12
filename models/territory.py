from models.db import get_db


def get_all_territories():
    return get_db().execute(
        "SELECT t.*, r.full_name AS rep_name FROM territories t "
        "LEFT JOIN reps r ON t.assigned_rep_id = r.id ORDER BY t.id"
    ).fetchall()


def get_territory_by_id(tid):
    return get_db().execute("SELECT * FROM territories WHERE id = ?", (tid,)).fetchone()


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
    db.execute("DELETE FROM territories WHERE id = ?", (tid,))
    db.commit()
