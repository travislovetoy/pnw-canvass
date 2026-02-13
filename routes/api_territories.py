from flask import Blueprint, request, jsonify
from routes.auth import login_required, admin_required
from models.territory import (
    get_all_territories, get_territory_by_id,
    create_territory, update_territory, delete_territory,
    assign_reps_to_territory, get_territory_reps,
)

bp = Blueprint("api_territories", __name__, url_prefix="/api")


@bp.route("/territories", methods=["GET"])
@login_required
def list_territories():
    territories = get_all_territories()
    result = []
    for t in territories:
        d = dict(t)
        d["rep_ids"] = [int(x) for x in d["rep_ids"].split(",")] if d.get("rep_ids") else []
        result.append(d)
    return jsonify(result)


@bp.route("/territories", methods=["POST"])
@admin_required
def add_territory():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("polygon_geojson"):
        return jsonify({"error": "name and polygon_geojson required"}), 400
    tid = create_territory(
        data["name"],
        data["polygon_geojson"],
        data.get("assigned_rep_id"),
        data.get("color", "#3388ff"),
    )
    rep_ids = data.get("rep_ids", [])
    if rep_ids:
        assign_reps_to_territory(tid, rep_ids)
    t = get_territory_by_id(tid)
    d = dict(t)
    d["rep_ids"] = rep_ids
    return jsonify(d), 201


@bp.route("/territories/<int:tid>", methods=["PUT"])
@admin_required
def edit_territory(tid):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    existing = get_territory_by_id(tid)
    if not existing:
        return jsonify({"error": "Not found"}), 404
    update_territory(
        tid,
        data.get("name", existing["name"]),
        data.get("polygon_geojson", existing["polygon_geojson"]),
        data.get("assigned_rep_id", existing["assigned_rep_id"]),
        data.get("color", existing["color"]),
    )
    t = get_territory_by_id(tid)
    return jsonify(dict(t))


@bp.route("/territories/<int:tid>/reps", methods=["PUT"])
@admin_required
def set_territory_reps(tid):
    data = request.get_json()
    if not data or "rep_ids" not in data:
        return jsonify({"error": "rep_ids required"}), 400
    existing = get_territory_by_id(tid)
    if not existing:
        return jsonify({"error": "Not found"}), 404
    assign_reps_to_territory(tid, data["rep_ids"])
    reps = get_territory_reps(tid)
    return jsonify({"ok": True, "reps": [dict(r) for r in reps]})


@bp.route("/territories/<int:tid>", methods=["DELETE"])
@admin_required
def remove_territory(tid):
    delete_territory(tid)
    return jsonify({"ok": True})
