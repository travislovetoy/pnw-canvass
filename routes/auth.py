from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from models.rep import get_rep_by_username, get_rep_by_id
import config

bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "rep_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "rep_id" not in session:
            return redirect(url_for("auth.login"))
        rep = get_rep_by_id(session["rep_id"])
        if not rep or not rep["is_admin"]:
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.map_view"))
        return f(*args, **kwargs)
    return decorated


@bp.route("/")
def index():
    if "rep_id" in session:
        return redirect(url_for("auth.map_view"))
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        rep = get_rep_by_username(username)
        if rep and check_password_hash(rep["password_hash"], password):
            session["rep_id"] = rep["id"]
            session["rep_name"] = rep["full_name"]
            session["is_admin"] = bool(rep["is_admin"])
            return redirect(url_for("auth.map_view"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@bp.route("/map")
@login_required
def map_view():
    return render_template("map.html", mapbox_token=config.MAPBOX_TOKEN)


@bp.route("/leads")
@login_required
def leads_view():
    return render_template("leads.html")


@bp.route("/leads/<int:lead_id>")
@login_required
def lead_detail_view(lead_id):
    return render_template("lead_detail.html", lead_id=lead_id)


@bp.route("/territories")
@login_required
def territories_view():
    return render_template("territories.html", mapbox_token=config.MAPBOX_TOKEN)


@bp.route("/reps")
@admin_required
def reps_view():
    return render_template("reps.html")


@bp.route("/dashboard")
@login_required
def dashboard_view():
    return render_template("dashboard.html")
