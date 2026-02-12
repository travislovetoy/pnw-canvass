from models.db import get_db


def get_all_reps():
    return get_db().execute("SELECT id, username, full_name, is_admin FROM reps ORDER BY id").fetchall()


def get_rep_by_id(rep_id):
    return get_db().execute("SELECT * FROM reps WHERE id = ?", (rep_id,)).fetchone()


def get_rep_by_username(username):
    return get_db().execute("SELECT * FROM reps WHERE username = ?", (username,)).fetchone()


def create_rep(username, password_hash, full_name, is_admin=0):
    db = get_db()
    db.execute(
        "INSERT INTO reps (username, password_hash, full_name, is_admin) VALUES (?, ?, ?, ?)",
        (username, password_hash, full_name, is_admin),
    )
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def update_rep(rep_id, full_name, is_admin):
    db = get_db()
    db.execute("UPDATE reps SET full_name = ?, is_admin = ? WHERE id = ?", (full_name, is_admin, rep_id))
    db.commit()


def update_rep_password(rep_id, password_hash):
    db = get_db()
    db.execute("UPDATE reps SET password_hash = ? WHERE id = ?", (password_hash, rep_id))
    db.commit()


def delete_rep(rep_id):
    db = get_db()
    db.execute("DELETE FROM reps WHERE id = ?", (rep_id,))
    db.commit()
