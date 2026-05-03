from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import login_required

from adapters.di import inject, FromDishka

from ..auth import AuthManager


bp = Blueprint("auth", __name__, url_prefix="/")


@bp.route("/login", methods=["GET", "POST"])
@inject
async def login(auth: FromDishka[AuthManager]) -> ResponseReturnValue:
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            if auth.login(username, password):
                return redirect(url_for("dashboard"))
            flash("Invalid login or password")
        else:
            flash("Both fields are required")

    return render_template("auth/login.html")


@bp.route("/logout", methods=["GET"])
@login_required
@inject
async def logout(auth: FromDishka[AuthManager]) -> ResponseReturnValue:
    auth.logout()
    return redirect(url_for("auth.login"))
