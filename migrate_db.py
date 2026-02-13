"""Add designation column to visits, service_type/service_tier to leads."""
import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "canvass.db"))


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check existing columns
    cols_visits = {row[1] for row in cur.execute("PRAGMA table_info(visits)").fetchall()}
    cols_leads = {row[1] for row in cur.execute("PRAGMA table_info(leads)").fetchall()}
    cols_reps = {row[1] for row in cur.execute("PRAGMA table_info(reps)").fetchall()}

    if "designation" not in cols_visits:
        cur.execute("ALTER TABLE visits ADD COLUMN designation TEXT DEFAULT 'not_home'")
        print("Added 'designation' column to visits.")
    else:
        print("'designation' column already exists in visits.")

    if "service_type" not in cols_leads:
        cur.execute("ALTER TABLE leads ADD COLUMN service_type TEXT DEFAULT ''")
        print("Added 'service_type' column to leads.")
    else:
        print("'service_type' column already exists in leads.")

    if "service_tier" not in cols_leads:
        cur.execute("ALTER TABLE leads ADD COLUMN service_tier TEXT DEFAULT ''")
        print("Added 'service_tier' column to leads.")
    else:
        print("'service_tier' column already exists in leads.")

    if "email" not in cols_reps:
        cur.execute("ALTER TABLE reps ADD COLUMN email TEXT")
        print("Added 'email' column to reps.")
    else:
        print("'email' column already exists in reps.")

    # Create territory_reps junction table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS territory_reps (
            territory_id INTEGER NOT NULL,
            rep_id INTEGER NOT NULL,
            PRIMARY KEY (territory_id, rep_id),
            FOREIGN KEY (territory_id) REFERENCES territories(id),
            FOREIGN KEY (rep_id) REFERENCES reps(id)
        )
    """)
    print("Ensured 'territory_reps' table exists.")

    # Migrate existing assigned_rep_id data into junction table
    cur.execute("""
        INSERT OR IGNORE INTO territory_reps (territory_id, rep_id)
        SELECT id, assigned_rep_id FROM territories
        WHERE assigned_rep_id IS NOT NULL
    """)
    migrated = cur.rowcount
    if migrated:
        print(f"Migrated {migrated} existing rep assignments to territory_reps.")

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
