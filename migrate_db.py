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

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()
