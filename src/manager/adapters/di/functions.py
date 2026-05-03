import asyncio
import inspect
from contextlib import AsyncExitStack
from functools import wraps
from typing import Any, Callable, cast, Coroutine, get_args, get_origin, Optional, TypeVar

from flask import Flask, g
from dishka import AsyncContainer, FromDishka, Scope


F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


def inject(f: F) -> F:
    sig = inspect.signature(f)

    hints = {
        name: get_args(param.annotation)[0]
        for name, param in sig.parameters.items()
        if get_origin(param.annotation) is FromDishka
    }

    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        container: AsyncContainer = getattr(g, "dishka_container")
        if not container:
            raise RuntimeError("Dishka container not found in flask.g. Did you forget setup_flask_async_dishka?")

        if hints:
            names = list(hints.keys())
            interfaces = [hints[name] for name in names]
            values = await asyncio.gather(*(container.get(iface) for iface in interfaces))

            for name, value in zip(names, values):
                kwargs[name] = value

        return await f(*args, **kwargs)
    setattr(wrapper, "__dishka_injected__", True)
    return cast(F, wrapper)


def setup_flask_async_dishka(app: Flask, container: AsyncContainer) -> None:
    setattr(app, "dishka_container", container)

    @app.before_request
    async def open_dishka_scope() -> None:
        stack = AsyncExitStack()
        context_manager = container(scope=Scope.REQUEST)
        request_container = await stack.enter_async_context(context_manager)
        setattr(g, "dishka_container", request_container)
        setattr(g, "dishka_exit_stack", stack)

    @app.teardown_request
    async def close_dishka_scope(_exception: Optional[BaseException] = None) -> None:
        stack = getattr(g, "dishka_exit_stack", None)
        if stack:
            await stack.aclose()

    @app.teardown_appcontext
    async def shutdown_dishka(_exception: Optional[BaseException] = None) -> None:
        app_container: Optional[AsyncContainer] = getattr(app, "dishka_container", None)
        if app_container:
            await app_container.close()


def verify_dishka_routes(app: Flask) -> None:
    for endpoint, view_func in app.view_functions.items():
        if hasattr(view_func, "view_class"):
            view_class = view_func.view_class

            for method_name in ("get", "post", "put", "delete", "patch",):
                method = getattr(view_class, method_name, None)
                if method:
                    _check_signature(endpoint, method)

        else:
            real_func = inspect.unwrap(view_func)
            _check_signature(endpoint, real_func)


def _check_signature(endpoint: str, func: Any) -> None:
    try:
        sig = inspect.signature(func)
    except (ValueError, TypeError):
        return

    has_dishka_params = any(
        get_origin(p.annotation) is FromDishka
        for p in sig.parameters.values()
    )

    if has_dishka_params and not hasattr(func, "__dishka_injected__"):
        raise RuntimeError(
            f"Error in route '{endpoint}' (method {func.__name__}): parameters detected FromDishka, "
            f"but forgotten decorator @inject. Without it, dependencies will not be injected."
        )
