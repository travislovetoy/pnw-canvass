from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from routes.auth import admin_required
from models.rep import get_all_reps, get_rep_by_id, create_rep, update_rep, update_rep_password, delete_rep

bp = Blueprint("api_reps", __name__, url_prefix="/api")


@bp.route("/reps", methods=["GET"])
@admin_required
def list_reps():
    reps = get_all_reps()
    return jsonify([dict(r) for r in reps])


@bp.route("/reps", methods=["POST"])
@admin_required
def add_rep():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password") or not data.get("full_name"):
        return jsonify({"error": "username, password, and full_name required"}), 400
    rep_id = create_rep(
        data["username"],
        generate_password_hash(data["password"], method="pbkdf2:sha256"),
        data["full_name"],
        int(data.get("is_admin", 0)),
    )
    return jsonify({"id": rep_id}), 201


@bp.route("/reps/<int:rep_id>", methods=["PUT"])
@admin_required
def edit_rep(rep_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    rep = get_rep_by_id(rep_id)
    if not rep:
        return jsonify({"error": "Not found"}), 404
    update_rep(rep_id, data.get("full_name", rep["full_name"]), int(data.get("is_admin", rep["is_admin"])))
    if data.get("password"):
        update_rep_password(rep_id, generate_password_hash(data["password"], method="pbkdf2:sha256"))
    return jsonify({"ok": True})


@bp.route("/reps/<int:rep_id>", methods=["DELETE"])
@admin_required
def remove_rep(rep_id):
    delete_rep(rep_id)
    return jsonify({"ok": True})
