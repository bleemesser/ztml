"""Pre-configured script tags for HTMX and common extensions.

Usage::

    from ztml import Html, Head, Body, Div
    from ztml.scripts import HTMX, HTMX_SSE

    Html(Head(HTMX, HTMX_SSE), Body(Div("hello")))
"""

from ztml._core import Script

HTMX = Script().src("https://unpkg.com/htmx.org/dist/htmx.min.js")
HTMX_SSE = Script().src("https://unpkg.com/htmx-ext-sse/sse.js")
HTMX_WS = Script().src("https://unpkg.com/htmx-ext-ws/ws.js")
HTMX_RESPONSE_TARGETS = Script().src(
    "https://unpkg.com/htmx-ext-response-targets/response-targets.js"
)
HTMX_HEAD_SUPPORT = Script().src(
    "https://unpkg.com/htmx-ext-head-support/head-support.js"
)
HTMX_PRELOAD = Script().src(
    "https://unpkg.com/htmx-ext-preload/preload.js"
)
