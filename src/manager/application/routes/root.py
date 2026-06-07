from flask import Blueprint, jsonify, render_template
from flask.typing import ResponseReturnValue


bp = Blueprint("root", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
async def home() -> ResponseReturnValue:
    return render_template("home.html")


@bp.route("health", methods=["GET"])
async def get_health() -> ResponseReturnValue:
    return jsonify({"status": "ok"}), 200
