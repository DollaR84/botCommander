from flask import Blueprint, jsonify
from flask.typing import ResponseReturnValue


bp = Blueprint("root", __name__, url_prefix="/")


@bp.route("health", methods=["GET"])
def get_health() -> ResponseReturnValue:
    return jsonify({"status": "ok"}), 200
