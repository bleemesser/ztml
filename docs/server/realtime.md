# Realtime: SSE and WebSockets

## HTMX scripts

Earlier versions of ztml auto-injected the HTMX script into every full-page response. I replaced that with explicit imports. It was convenient but made it hard to reason about what was actually in your page, and didn't extend cleanly to HTMX extensions. Now you import what you need and drop them in your `Head()`.

```python
from ztml.scripts import HTMX, HTMX_SSE, HTMX_WS

Html(
    Head(Title("My App"), HTMX, HTMX_SSE),
    Body(...)
)
```

Available exports:

- `HTMX`: the core HTMX library
- `HTMX_SSE`: the SSE extension
- `HTMX_WS`: the WebSocket extension
- `HTMX_RESPONSE_TARGETS`: response targets extension
- `HTMX_HEAD_SUPPORT`: head element support
- `HTMX_PRELOAD`: link preloading

These are just `Script` elements pointing at unpkg CDN URLs. If you'd rather pin a version or self-host, use your own `Script().src(...)` instead.

## Server-Sent Events

### EventStream

`EventStream` wraps an async generator into an SSE response. Each yielded item is rendered and sent as an unnamed `data:` event.

```python
from ztml.server import ZTMLApp, EventStream, serve

app = ZTMLApp()

@app.route("/stream")
async def get():
    async def updates():
        yield Div("first update")
        yield Div("second update")
    return EventStream(updates()).response()
```

### NamedEventStream

For multiple named event sources with independent intervals, `NamedEventStream` is more ergonomic. Register sources with decorators and they run on their own schedules.

```python
from ztml.server import NamedEventStream

clock = NamedEventStream(interval=1)

@clock.source("time")
def time_event():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

@clock.source("date", interval=60)
def date_event():
    from datetime import datetime
    return datetime.now().strftime("%A, %B %d, %Y")

@app.route("/clock")
async def clock_route():
    return clock.response()
```

On the client side, use HTMX's SSE extension to connect and swap content by event name:

```python
from ztml.scripts import HTMX, HTMX_SSE

# In Head()
Head(Title("Clock"), HTMX, HTMX_SSE)

# In Body()
Div(
    Div("--:--:--").id("time").attr("sse-swap", "time"),
    Div("---").id("date").attr("sse-swap", "date"),
).hx_ext("sse").attr("sse-connect", "/clock")
```

Sources can be sync or async, and can return elements, components, or strings.

## WebSockets

The `@app.ws()` decorator registers a WebSocket endpoint. You get the raw Starlette `WebSocket` object.

```python
@app.ws("/echo")
async def echo(websocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(f"echo: {data}")
    await websocket.close()
```

Path parameters work the same as with HTTP routes:

```python
@app.ws("/chat/{room}")
async def chat(websocket, room):
    await websocket.accept()
    # ...
```

WebSocket handlers are lower-level than SSE—you manage the connection lifecycle yourself. For most cases where you're pushing server updates to the page, SSE with HTMX is simpler.
