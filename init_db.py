#!/usr/bin/env python3
import sqlite3
import os
from werkzeug.security import generate_password_hash
import config


def init():
    db = sqlite3.connect(config.DB_PATH)
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        db.executescript(f.read())

    # Seed admin user if not exists
    existing = db.execute("SELECT id FROM reps WHERE username = 'admin'").fetchone()
    if not existing:
        db.execute(
            "INSERT INTO reps (username, password_hash, full_name, is_admin) VALUES (?, ?, ?, ?)",
            ("admin", generate_password_hash("admin", method="pbkdf2:sha256"), "Admin User", 1),
        )
        db.commit()
        print("Seeded admin user (admin / admin)")
    else:
        print("Admin user already exists")

    db.close()
    print(f"Database initialized at {config.DB_PATH}")


if __name__ == "__main__":
    init()
