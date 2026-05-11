import asyncio
import inspect
from contextlib import AsyncExitStack
from functools import wraps
from typing import Annotated, Any, Callable, cast, Coroutine, get_args, get_origin, Optional, TypeVar

from flask import Flask, g
from dishka import AsyncContainer, Scope


F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


def _extract_dishka_hints(func: Any) -> dict[str, Any]:
    hints: dict[str, Any] = {}
    target = inspect.unwrap(func)
    sig = inspect.signature(target)

    for name, param in sig.parameters.items():
        annotation = param.annotation

        if get_origin(annotation) is not Annotated:
            continue

        annotated_args = get_args(annotation)
        if not annotated_args or len(annotated_args) < 2:
            continue

        hint_type, *metadata = annotated_args

        for m in metadata:
            if type(m).__name__ == "_FromComponent" or m.__class__.__name__ == "_FromComponent":
                hints[name] = hint_type
                break

    return hints


def inject(f: F) -> F:
    target = inspect.unwrap(f)
    hints = _extract_dishka_hints(target)

    @wraps(f)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        container: AsyncContainer = getattr(g, "dishka_container")
        if container is None:
            raise RuntimeError("Dishka container not found in flask.g. Did you forget setup_flask_async_dishka?")

        if hints:
            unfilled_hints = {k: v for k, v in hints.items() if k not in kwargs}
            if unfilled_hints:
                names = list(unfilled_hints.keys())
                interfaces = [unfilled_hints[name] for name in names]
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
        root_container: AsyncContainer = getattr(app, "dishka_container")
        if not root_container:
            raise RuntimeError("flask app has no attribute dishka_container")

        stack = AsyncExitStack()
        context_manager = root_container(scope=Scope.REQUEST)
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
            _check_signature(endpoint, view_func)


def _check_signature(endpoint: str, func: Any) -> None:
    try:
        hints = _extract_dishka_hints(func)
    except (ValueError, TypeError, NameError):
        return

    if hints and not hasattr(func, "__dishka_injected__"):
        raise RuntimeError(
            f"Error in route '{endpoint}' (method {func.__name__}): "
            f"parameters detected FromDishka, "
            f"but forgotten decorator @inject. "
            f"Without it, dependencies will not be injected."
        )
