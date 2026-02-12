from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.lead import (
    get_all_leads, get_lead_by_id, create_lead, update_lead,
    update_lead_stage, mark_uisp_synced, mark_uisp_failed, delete_lead,
)
from services.uisp_client import push_lead_to_uisp

bp = Blueprint("api_leads", __name__, url_prefix="/api")


@bp.route("/leads", methods=["GET"])
@login_required
def list_leads():
    filters = {}
    for key in ("pipeline_stage", "rep_id", "territory_id"):
        val = request.args.get(key)
        if val:
            filters[key] = val
    leads = get_all_leads(filters)
    return jsonify([dict(l) for l in leads])


@bp.route("/leads", methods=["POST"])
@login_required
def add_lead():
    data = request.get_json()
    if not data or not data.get("first_name") or not data.get("last_name"):
        return jsonify({"error": "first_name and last_name are required"}), 400
    data["created_by_rep_id"] = session["rep_id"]
    lead_id = create_lead(data)
    lead = get_lead_by_id(lead_id)

    # Auto-push to UISP
    uisp_id, err = push_lead_to_uisp(dict(lead))
    if uisp_id:
        mark_uisp_synced(lead_id, uisp_id)
    elif err:
        mark_uisp_failed(lead_id)

    lead = get_lead_by_id(lead_id)
    return jsonify(dict(lead)), 201


@bp.route("/leads/<int:lead_id>", methods=["GET"])
@login_required
def get_lead(lead_id):
    lead = get_lead_by_id(lead_id)
    if not lead:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(lead))


@bp.route("/leads/<int:lead_id>", methods=["PUT"])
@login_required
def edit_lead(lead_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data"}), 400
    update_lead(lead_id, data)
    lead = get_lead_by_id(lead_id)
    return jsonify(dict(lead))


@bp.route("/leads/<int:lead_id>/stage", methods=["PUT"])
@login_required
def change_stage(lead_id):
    data = request.get_json()
    stage = data.get("pipeline_stage") if data else None
    if not stage:
        return jsonify({"error": "pipeline_stage required"}), 400
    try:
        update_lead_stage(lead_id, stage)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"ok": True})


@bp.route("/leads/<int:lead_id>/sync", methods=["POST"])
@login_required
def retry_sync(lead_id):
    lead = get_lead_by_id(lead_id)
    if not lead:
        return jsonify({"error": "Not found"}), 404
    uisp_id, err = push_lead_to_uisp(dict(lead))
    if uisp_id:
        mark_uisp_synced(lead_id, uisp_id)
        return jsonify({"ok": True, "uisp_client_id": uisp_id})
    mark_uisp_failed(lead_id)
    return jsonify({"error": err}), 502


@bp.route("/leads/<int:lead_id>", methods=["DELETE"])
@login_required
def remove_lead(lead_id):
    delete_lead(lead_id)
    return jsonify({"ok": True})
