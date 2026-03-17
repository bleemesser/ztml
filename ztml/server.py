from __future__ import annotations

import asyncio
import inspect
import re
import time
from typing import Any, AsyncGenerator, Callable

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response, StreamingResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from ztml._core import render

HTMX_SCRIPT = '<script src="https://unpkg.com/htmx.org"></script>'

RELOAD_SCRIPT = """<script>
(function(){var s=new WebSocket("ws://"+location.host+"/_ztml/reload");
s.onclose=function(){setTimeout(function(){location.reload()},300)};})();
</script>"""

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


def _render_obj(obj: Any) -> str:
    if isinstance(obj, str):
        return obj
    return render(obj)


def _inject_head(html: str, *, dev: bool = False) -> str:
    lower = html.lstrip().lower()
    if not lower.startswith("<html") and not lower.startswith("<!doctype"):
        return html
    scripts = ""
    if "htmx.org" not in html:
        scripts += HTMX_SCRIPT
    if dev:
        scripts += RELOAD_SCRIPT
    if not scripts:
        return html
    match = re.search(r"<head[^>]*>", html, re.IGNORECASE)
    if match:
        pos = match.end()
        return html[:pos] + scripts + html[pos:]
    return html


def _resolve_kwargs(params: list[str], request: Request) -> dict[str, Any]:
    kwargs: dict[str, Any] = {}
    for name in params:
        if name == "request":
            kwargs[name] = request
        elif name == "session":
            kwargs[name] = request.session
        elif name in request.path_params:
            kwargs[name] = request.path_params[name]
    return kwargs


async def _resolve_form_kwargs(
    params: list[str], request: Request, kwargs: dict[str, Any]
) -> None:
    wants_form = "form_data" in params
    wants_files = "files" in params
    if not wants_form and not wants_files:
        return
    form = await request.form()
    if wants_form:
        kwargs["form_data"] = form
    if wants_files:
        kwargs["files"] = form


def _make_endpoint(
    handler: Callable, *, before: list[Callable] | None = None, dev: bool = False
) -> Callable:
    sig = inspect.signature(handler)
    params = list(sig.parameters.keys())

    before_specs: list[tuple[Callable, list[str]]] = []
    if before:
        for hook in before:
            hook_sig = inspect.signature(hook)
            before_specs.append((hook, list(hook_sig.parameters.keys())))

    async def endpoint(request: Request) -> Response:
        for hook, hook_params in before_specs:
            hook_kwargs = _resolve_kwargs(hook_params, request)
            await _resolve_form_kwargs(hook_params, request, hook_kwargs)
            if inspect.iscoroutinefunction(hook):
                hook_result = await hook(**hook_kwargs)
            else:
                hook_result = hook(**hook_kwargs)
            if isinstance(hook_result, Response):
                return hook_result

        kwargs = _resolve_kwargs(params, request)
        await _resolve_form_kwargs(params, request, kwargs)

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

        html = _inject_head(html, dev=dev)
        return HTMLResponse(html)

    return endpoint


class EventStream:
    """Wrap an async generator of ztml components into an SSE StreamingResponse.

    Each yielded item is rendered and sent as an unnamed SSE ``data:`` event.
    Multiline output is split across multiple ``data:`` lines per the SSE spec.

    Usage::

        async def counter():
            i = 0
            while True:
                yield Div(str(i))
                i += 1
                await asyncio.sleep(1)

        @app.route("/stream")
        async def stream():
            return EventStream(counter()).response()
    """

    def __init__(self, generator: AsyncGenerator, limit: int = 0) -> None:
        self._gen = generator
        self._limit = limit

    async def _stream(self) -> AsyncGenerator[str, None]:
        emitted = 0
        async for item in self._gen:
            data = _render_obj(item)
            for line in data.splitlines():
                yield f"data: {line}\n"
            yield "\n"
            emitted += 1
            if self._limit and emitted >= self._limit:
                return

    def response(self) -> StreamingResponse:
        return StreamingResponse(self._stream(), media_type="text/event-stream")


class NamedEventStream:
    """SSE stream with multiple named event sources, each rendered automatically.

    Register source functions with :meth:`source`. Each source returns a ztml
    component (or string) that gets rendered, newline-stripped, and framed as a
    named SSE event. Sources can be sync or async.

    Sources share a default interval but can override it individually. Sources
    with different intervals are tracked independently via last-fired timestamps.

    Usage::

        stream = NamedEventStream(interval=2)

        @stream.source("cpu")
        def cpu_event():
            return cpu_fragment()

        @stream.source("logs", interval=5)
        async def logs_event():
            return await fetch_recent_logs()

        @app.route("/stream")
        async def stream_route():
            return stream.response()

    On the client side, use ``sse-swap`` attributes matching the event names::

        Div("Loading...").id("cpu").attr("sse-swap", "cpu")
    """

    def __init__(self, interval: float = 1, limit: int = 0) -> None:
        self._default_interval = interval
        self._sources: list[tuple[str, Callable, float]] = []
        self._limit = limit

    def source(self, name: str, *, interval: float | None = None) -> Callable:
        """Register a named event source.

        Args:
            name: The SSE event name (matches ``sse-swap`` on the client).
            interval: Seconds between invocations. Defaults to the stream-level
                interval.
        """
        ival = interval if interval is not None else self._default_interval

        def decorator(fn: Callable) -> Callable:
            self._sources.append((name, fn, ival))
            return fn

        return decorator

    async def _stream(self) -> AsyncGenerator[str, None]:
        last_fired: dict[str, float] = {name: 0.0 for name, _, _ in self._sources}
        emitted = 0
        while True:
            now = time.monotonic()
            fired_any = False
            for name, fn, ival in self._sources:
                if now - last_fired[name] >= ival:
                    if asyncio.iscoroutinefunction(fn):
                        result = await fn()
                    else:
                        result = fn()
                    data = _render_obj(result).replace("\n", "")
                    yield f"event: {name}\ndata: {data}\n\n"
                    last_fired[name] = now
                    fired_any = True
                    emitted += 1
                    if self._limit and emitted >= self._limit:
                        return
            if not fired_any:
                await asyncio.sleep(0.1)
            else:
                # Sleep for the shortest remaining interval
                next_fire = min(
                    ival - (now - last_fired[name])
                    for name, _, ival in self._sources
                )
                await asyncio.sleep(max(next_fire, 0.05))

    def response(self) -> StreamingResponse:
        """Return a ``StreamingResponse`` suitable for returning from a route."""
        return StreamingResponse(self._stream(), media_type="text/event-stream")


class ZTMLApp:
    def __init__(self, *, session_secret: str | None = None, dev: bool = False) -> None:
        self._routes: list[Route] = []
        self._ws_routes: list[WebSocketRoute] = []
        self._app: Starlette | None = None
        self._session_secret = session_secret
        self._dev = dev

    def route(
        self,
        path: str,
        methods: list[str] | None = None,
        *,
        before: list[Callable] | None = None,
    ) -> Callable:
        def decorator(fn: Callable) -> Callable:
            m = methods
            if m is None:
                name = fn.__name__.lower()
                m = [name.upper()] if name in HTTP_METHODS else ["GET"]
            self._routes.append(
                Route(path, _make_endpoint(fn, before=before, dev=self._dev), methods=m)
            )
            self._app = None
            return fn
        return decorator

    def ws(self, path: str) -> Callable:
        def decorator(fn: Callable) -> Callable:
            sig = inspect.signature(fn)
            params = list(sig.parameters.keys())

            async def ws_endpoint(websocket: WebSocket) -> None:
                kwargs: dict[str, Any] = {}
                for name in params:
                    if name in ("websocket", "ws"):
                        kwargs[name] = websocket
                    elif name in websocket.path_params:
                        kwargs[name] = websocket.path_params[name]
                if inspect.iscoroutinefunction(fn):
                    await fn(**kwargs)
                else:
                    fn(**kwargs)

            self._ws_routes.append(WebSocketRoute(path, ws_endpoint))
            self._app = None
            return fn
        return decorator

    def _build(self) -> Starlette:
        if self._app is None:
            routes = list(self._routes) + list(self._ws_routes)
            if self._dev:
                async def _reload_ws(websocket: WebSocket) -> None:
                    await websocket.accept()
                    try:
                        while True:
                            await websocket.receive_text()
                    except WebSocketDisconnect:
                        pass
                routes.append(WebSocketRoute("/_ztml/reload", _reload_ws))

            middleware = []
            if self._session_secret:
                middleware.append(
                    Middleware(SessionMiddleware, secret_key=self._session_secret)
                )
            self._app = Starlette(routes=routes, middleware=middleware)
        return self._app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        app = self._build()
        await app(scope, receive, send)


# Default app instance for the rt/ws/serve convenience API
app = ZTMLApp()


def rt(
    path: str,
    methods: list[str] | None = None,
    *,
    before: list[Callable] | None = None,
) -> Callable:
    return app.route(path, methods, before=before)


def ws(path: str) -> Callable:
    return app.ws(path)


def serve(
    host: str = "localhost",
    port: int = 5001,
    *,
    target: ZTMLApp | None = None,
    **kwargs: Any,
) -> None:
    import sys
    import uvicorn

    the_app = target or app

    if the_app._dev:
        # uvicorn reload requires a string import path, not an app instance.
        import pathlib
        caller = sys._getframe(1)
        script = pathlib.Path(caller.f_globals["__file__"]).resolve()

        # Find the variable name that holds the app in the caller's module
        var = "app"
        for k, v in caller.f_globals.items():
            if v is the_app:
                var = k
                break

        # Ensure the script's directory is importable in this process and subprocesses
        import os
        script_dir = str(script.parent)
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        pp = os.environ.get("PYTHONPATH", "")
        if script_dir not in pp.split(os.pathsep):
            os.environ["PYTHONPATH"] = script_dir + (os.pathsep + pp if pp else "")

        app_path = f"{script.stem}:{var}"
        kwargs.setdefault("reload", True)
        kwargs.setdefault("reload_dirs", [script_dir])
        uvicorn.run(app_path, host=host, port=port, **kwargs)
    else:
        uvicorn.run(the_app, host=host, port=port, **kwargs)
