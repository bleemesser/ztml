# ztml

A Rust-backed framework for building websites in pure Python. Define HTML, CSS, and JS using Python expressions with full autocompletion support. Inspired by [FastHTML](https://fastht.ml/).

## Install

```bash
pip install ztml            # Core HTML/CSS/JS rendering
pip install ztml[serve]     # Include the built-in web server
```

## First look

```python
from ztml import *

page = render(
    Html(
        Head(Meta().charset("utf-8"), Title("My App")),
        Body(
            H1("Hello, ztml!"),
            P("Build websites with Python.").cls("intro"),
            A("GitHub").href("https://github.com").target("_blank"),
        ),
    )
)
```

Every HTML element has a constructor. Attributes are set via chained builder methods. The Rust core handles rendering, and a 6K-line `.pyi` stub gives you autocomplete and type-checking in your editor.

## What's provided

150+ HTML element constructors, CSS-in-Python via `Rule`, `Media`, and `Keyframes` with 400+ typed property methods generated from W3C specs, JavaScript helpers for event handling, a component protocol based on `__ztml_render__`, and HTMX integration via pre-configured script tags. The optional `serve` extra adds a built-in server with routing, sessions, SSE, and WebSocket support.
