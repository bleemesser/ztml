from __future__ import annotations

import inspect
import re
from typing import Any, Callable, Sequence

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import Route

from ztml._core import render, Element, Fragment, Style, Script

HTMX_SCRIPT = '<script src="https://unpkg.com/htmx.org"></script>'

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _render_obj(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    return render(obj)


def _inject_htmx(html: str) -> str:
    if not html.lstrip().lower().startswith("<html") and not html.lstrip().lower().startswith("<!doctype"):
        return html
    if "htmx.org" in html:
        return html
    match = re.search(r"</head>", html, re.IGNORECASE)
    if match:
        return html[: match.start()] + HTMX_SCRIPT + html[match.start() :]
    return html


def _make_endpoint(handler: Callable) -> Callable:
    sig = inspect.signature(handler)
    params = list(sig.parameters.keys())

    async def endpoint(request: Request) -> Response:
        kwargs = {}
        for name in params:
            if name == "request":
                kwargs[name] = request
            elif name in request.path_params:
                kwargs[name] = request.path_params[name]

        if inspect.iscoroutinefunction(handler):
            result = await handler(**kwargs)
        else:
            result = handler(**kwargs)

        if isinstance(result, Response):
            return result

        if isinstance(result, tuple):
            html = "".join(_render_obj(item) for item in result)
        else:
            html = _render_obj(result)

        html = _inject_htmx(html)
        return HTMLResponse(html)

    return endpoint


class ZTMLApp:
    def __init__(self) -> None:
        self._routes: list[Route] = []
        self._app: Starlette | None = None

    def route(self, path: str, methods: list[str] | None = None) -> Callable:
        def decorator(fn: Callable) -> Callable:
            m = methods
            if m is None:
                name = fn.__name__.lower()
                m = [name.upper()] if name in HTTP_METHODS else ["GET"]
            self._routes.append(Route(path, _make_endpoint(fn), methods=m))
            self._app = None  # invalidate cached app
            return fn
        return decorator

    def _build(self) -> Starlette:
        if self._app is None:
            self._app = Starlette(routes=list(self._routes))
        return self._app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        app = self._build()
        await app(scope, receive, send)


# Default app instance
app = ZTMLApp()


def rt(path: str, methods: list[str] | None = None) -> Callable:
    return app.route(path, methods)


def serve(host: str = "localhost", port: int = 5001) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port)
