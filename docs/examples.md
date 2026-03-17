# Examples

The `examples/` directory in the repo has working demos covering different parts of the library. You can run any of them with `uv run`.

## Static page

Generates an HTML file to stdout. No server involved, just elements, styles, keyframe animations, and event handlers. Pipe to a file and open with your browser to view.

```bash
uv run examples/static_page.py > page.html
```

## Counter

An HTMX-powered counter with increment, decrement, and reset buttons. Good starting point for understanding how HTMX partial responses work with ztml.

```bash
uv run examples/counter_server.py
```

## Todo app

Full CRUD todo list with add, toggle, and delete. Demonstrates form handling, path parameters, and `Fragment` for returning multiple elements.

```bash
uv run examples/todo_server.py
```

## Custom components

Shows the `__ztml_render__` protocol with Card, Badge, NavLink, and Page components. Renders to a static HTML file.

```bash
uv run examples/components.py > components.html
```

## Auth demo

Sessions, before hooks, and form data parsing. Has a login page, a protected dashboard, and logout. Shows how `require_auth` works as a before hook.

```bash
uv run examples/auth_app.py
```

## WebSocket chat

A chat room using raw WebSockets. Multiple clients can connect and broadcast messages. The client-side code uses `RawJs` and `On` event handlers.

```bash
uv run examples/ws_chat.py
```

## SSE clock

A live-updating clock using `NamedEventStream` with two sources running at different intervals. Shows HTMX SSE extension integration.

```bash
uv run examples/sse_clock.py
```

## Jupyter notebook

`examples/notebook_demo.ipynb` demonstrates interactive development in Jupyter, including `_repr_html_()` rendering and building styled components inline.
