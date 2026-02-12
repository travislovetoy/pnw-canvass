from flask import Blueprint, jsonify
from routes.auth import login_required
from models.db import get_db

bp = Blueprint("api_dashboard", __name__, url_prefix="/api")


@bp.route("/dashboard/stats", methods=["GET"])
@login_required
def stats():
    db = get_db()

    stage_counts = {}
    for row in db.execute("SELECT pipeline_stage, COUNT(*) as cnt FROM leads GROUP BY pipeline_stage").fetchall():
        stage_counts[row["pipeline_stage"]] = row["cnt"]

    visit_counts = {}
    for row in db.execute("SELECT status, COUNT(*) as cnt FROM visits GROUP BY status").fetchall():
        visit_counts[row["status"]] = row["cnt"]

    visits_by_rep = []
    for row in db.execute(
        "SELECT r.full_name, COUNT(v.id) as cnt FROM visits v "
        "JOIN reps r ON v.rep_id = r.id GROUP BY v.rep_id ORDER BY cnt DESC"
    ).fetchall():
        visits_by_rep.append({"rep": row["full_name"], "count": row["cnt"]})

    total_leads = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_visits = db.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
    synced = db.execute("SELECT COUNT(*) FROM leads WHERE uisp_synced = 1").fetchone()[0]
    failed = db.execute("SELECT COUNT(*) FROM leads WHERE uisp_synced = -1").fetchone()[0]

    return jsonify({
        "stage_counts": stage_counts,
        "visit_counts": visit_counts,
        "visits_by_rep": visits_by_rep,
        "total_leads": total_leads,
        "total_visits": total_visits,
        "uisp_synced": synced,
        "uisp_failed": failed,
    })
