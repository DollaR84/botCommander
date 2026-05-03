import asyncio

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask.views import MethodView
from flask.typing import ResponseReturnValue
from flask_login import login_required

from adapters.di import inject, FromDishka
from application import dto, interactors
from db.admin import AdminDbConnector
from services.docker import DockerService
from services.builder import EnvBuilder
from services.types import ImageType, RestartPolicyType


bp = Blueprint("bots", __name__, url_prefix="/bots")


class BotManagerView(MethodView):

    @login_required
    @inject
    async def get(
            self,
            getter: FromDishka[interactors.GetBots],
            docker: FromDishka[DockerService],
    ) -> ResponseReturnValue:
        bots = await getter()

        stats_results = await asyncio.gather(*(docker.get_stats(bot) for bot in bots))
        stats = dict(zip([bot.id for bot in bots], stats_results))

        return render_template("bots/index.html", bots=bots, stats=stats)

    @login_required
    @inject
    async def post(
            self,
            creater: FromDishka[interactors.CreateBot],
            getter: FromDishka[interactors.GetBot],
            admin: FromDishka[AdminDbConnector],
            docker: FromDishka[DockerService],
            env_builder: FromDishka[EnvBuilder],
    ) -> ResponseReturnValue:
        url = request.form.get("url")
        token = request.form.get("token")
        if url and token:
            data = dto.CreateBot(
                url=url,
                token=token,
                branch=request.form.get("branch", "main"),
                bot_name=request.form.get("bot_name"),
                image_type=ImageType(request.form.get("image_type", "base")),
                mem_reservation=int(request.form.get("mem_reservation", 20)),
                mem_limit=int(request.form.get("mem_limit", 64)),
                cpu_quota_percents=int(request.form.get("cpu_quota", 20)),
                cpu_period_percents=int(request.form.get("cpu_period", 100)),
                restart_policy=RestartPolicyType(request.form.get("restart_policy", "unless-stopped")),
                is_active=True
            )
            need_db = request.form.get("need_db", False)
            data.extra_env["NEED_DB"] = "1" if need_db else "0"
            data.extra_env |= env_builder.data

            bot_id = await creater(data)
            bot = await getter(bot_id)
            if not bot:
                return jsonify({"message": f"bot with id={bot_id} not found"}), 404

            await docker.download(bot)
            if need_db:
                await admin.prepare_bot_db_environment(bot)
            return render_template("bots/details.html", bot=bot)

        flash("url and token fields are required")
        return redirect(url_for("bots.manager"))


class BotControllerView(MethodView):

    @login_required
    @inject
    async def get(self, bot_id: int, getter: FromDishka[interactors.GetBot]) -> ResponseReturnValue:
        bot = await getter(bot_id)
        if not bot:
            return jsonify({"status": "error", "message": "Not Found"}), 404

        return render_template("bots/details.html", bot=bot)

    @login_required
    @inject
    async def put(
            self,
            bot_id: int,
            getter: FromDishka[interactors.GetBot],
            updater: FromDishka[interactors.UpdateBot],
            admin: FromDishka[AdminDbConnector],
    ) -> ResponseReturnValue:
        bot = await getter(bot_id)
        if not bot:
            return jsonify({"status": "error", "message": "Not Found"}), 404

        mem_reservation = request.json.get("mem_reservation")
        mem_limit = request.json.get("mem_limit")
        cpu_quota_percents = request.json.get("cpu_quota")
        cpu_period_percents = request.json.get("cpu_period")
        restart_policy = request.json.get("restart_policy")

        data = dto.UpdateBot(
            url=request.json.get("url"),
            branch=request.json.get("branch"),
            token=request.json.get("token"),
            mem_reservation=int(mem_reservation) if mem_reservation else None,
            mem_limit=int(mem_limit) if mem_limit else None,
            cpu_quota_percents=int(cpu_quota_percents) if cpu_quota_percents else None,
            cpu_period_percents=int(cpu_period_percents) if cpu_period_percents else None,
            restart_policy=RestartPolicyType(restart_policy) if restart_policy else None,
            extra_env=request.json.get("extra_env"),
            is_active=request.json.get("is_active"),
        )

        need_db = request.json.get("need_db", False)
        if need_db != bot.need_db:
            bot.extra_env["NEED_DB"] = "1" if need_db else "0"
            data.extra_env = bot.extra_env
            await admin.prepare_bot_db_environment(bot)

        update_bot_id = await updater(bot_id, data)
        return jsonify({"status": "success", "message": f"update data bot id={update_bot_id}"})

    @login_required
    @inject
    async def delete(
            self,
            bot_id: int,
            getter: FromDishka[interactors.GetBot],
            deliter: FromDishka[interactors.DeleteBot],
            docker: FromDishka[DockerService],
            admin: FromDishka[AdminDbConnector],
    ) -> ResponseReturnValue:
        bot = await getter(bot_id)
        if not bot:
            return jsonify({"status": "error", "message": "Not Found"}), 404

        await docker.stop(bot)
        bot.extra_env["NEED_DB"] = "0"
        await admin.prepare_bot_db_environment(bot)
        await deliter(bot_id)
        return jsonify({"status": "success", "message": f"delete bot id={bot_id}"})


@bp.route("/<int:bot_id>/<action>", methods=["POST"])
@login_required
@inject
async def bot_runner(
        bot_id: int,
        action: str,
        getter: FromDishka[interactors.GetBot],
        docker: FromDishka[DockerService],
) -> ResponseReturnValue:
    bot = await getter(bot_id)
    if not bot:
        return jsonify({"status": "error", "message": f"bot id={bot_id} not Found"}), 404

    status = False
    if action == "start":
        result = await docker.start(bot)
    elif action == "stop":
        result = await docker.stop(bot)
    else:
        return jsonify({"status": "error", "message": f"invalid action '{action}'"}), 400

    resp_obj = result[0] if isinstance(result, tuple) else result
    data = resp_obj.get_json()
    status = data["status"] == "started" if data else False
    return jsonify({"success": status})


@bp.route("/<action>", methods=["POST"])
@login_required
@inject
async def service(
        action: str,
        getter: FromDishka[interactors.GetBots],
        docker: FromDishka[DockerService],
) -> ResponseReturnValue:
    if action == "prune":
        return await docker.prune()

    if action == "sync":
        bots = await getter()
        await docker.sync_bots(bots)
        return jsonify({"message": "Sync completed"})

    return jsonify({"message": "invalid action type"}), 404


@bp.route("/<int:bot_id>/git-update", methods=["POST"])
@login_required
@inject
async def git_update_bot(
        bot_id: int,
        getter: FromDishka[interactors.GetBot],
        docker: FromDishka[DockerService],
) -> ResponseReturnValue:
    bot = await getter(bot_id)
    if not bot:
        return jsonify({"message": f"bot with id={bot_id} not found"}), 404

    return await docker.update(bot)


@bp.route("/<int:bot_id>/logs", methods=["GET"])
@login_required
@inject
async def get_bot_logs(
        bot_id: int,
        getter: FromDishka[interactors.GetBot],
        docker: FromDishka[DockerService],
) -> ResponseReturnValue:
    bot = await getter(bot_id)
    if not bot:
        return jsonify({"message": f"bot with id={bot_id} not found"}), 404

    return await docker.get_logs(bot)


bp.add_url_rule("/", view_func=BotManagerView.as_view("manager"))
bp.add_url_rule("/<int:bot_id>", view_func=BotControllerView.as_view("controller"))
