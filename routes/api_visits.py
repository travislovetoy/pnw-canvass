from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.visit import get_all_visits, get_visit_by_id, create_visit, update_visit, delete_visit

bp = Blueprint("api_visits", __name__, url_prefix="/api")


@bp.route("/visits", methods=["GET"])
@login_required
def list_visits():
    filters = {}
    for key in ("rep_id", "status", "designation", "territory_id", "date_from", "date_to"):
        val = request.args.get(key)
        if val:
            filters[key] = val
    visits = get_all_visits(filters)
    return jsonify([dict(v) for v in visits])


@bp.route("/visits", methods=["POST"])
@login_required
def add_visit():
    data = request.get_json()
    if not data or data.get("lat") is None or data.get("lon") is None:
        return jsonify({"error": "lat and lon are required"}), 400
    data["rep_id"] = session["rep_id"]
    visit_id = create_visit(data)
    visit = get_visit_by_id(visit_id)
    return jsonify(dict(visit)), 201


@bp.route("/visits/<int:visit_id>", methods=["PUT"])
@login_required
def edit_visit(visit_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    update_visit(visit_id, data)
    visit = get_visit_by_id(visit_id)
    return jsonify(dict(visit))


@bp.route("/visits/<int:visit_id>", methods=["DELETE"])
@login_required
def remove_visit(visit_id):
    delete_visit(visit_id)
    return jsonify({"ok": True})
