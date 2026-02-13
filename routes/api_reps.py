import string
import secrets
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from routes.auth import admin_required
from models.rep import get_all_reps, get_rep_by_id, create_rep, update_rep, update_rep_password, delete_rep
from services.email_client import send_welcome_email
import config

bp = Blueprint("api_reps", __name__, url_prefix="/api")


def _generate_password(length=8):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@bp.route("/reps", methods=["GET"])
@admin_required
def list_reps():
    reps = get_all_reps()
    return jsonify([dict(r) for r in reps])


@bp.route("/reps", methods=["POST"])
@admin_required
def add_rep():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("full_name") or not data.get("email"):
        return jsonify({"error": "username, full_name, and email required"}), 400

    password = _generate_password()
    rep_id = create_rep(
        data["username"],
        generate_password_hash(password, method="pbkdf2:sha256"),
        data["full_name"],
        int(data.get("is_admin", 0)),
        email=data["email"],
    )

    login_url = config.APP_URL.rstrip("/") + "/login"
    email_ok, email_err = send_welcome_email(
        data["email"], data["full_name"], data["username"], password, login_url
    )

    return jsonify({"id": rep_id, "email_sent": email_ok, "email_error": email_err}), 201


@bp.route("/reps/<int:rep_id>", methods=["PUT"])
@admin_required
def edit_rep(rep_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    rep = get_rep_by_id(rep_id)
    if not rep:
        return jsonify({"error": "Not found"}), 404
    update_rep(
        rep_id,
        data.get("full_name", rep["full_name"]),
        int(data.get("is_admin", rep["is_admin"])),
        email=data.get("email", rep["email"]),
    )
    if data.get("password"):
        update_rep_password(rep_id, generate_password_hash(data["password"], method="pbkdf2:sha256"))
    return jsonify({"ok": True})


@bp.route("/reps/<int:rep_id>", methods=["DELETE"])
@admin_required
def remove_rep(rep_id):
    delete_rep(rep_id)
    return jsonify({"ok": True})
