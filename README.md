# ztml

A Rust-backed framework for building websites in pure Python. Define HTML, CSS, and JS using Python expressions with full autocompletion. Inspired by [FastHTML](https://fastht.ml/).

**Read my [documentation](https://bleemesser.github.io/ztml/)**

## Install

```bash
pip install ztml
```

## Quick example

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

Every HTML element has a constructor. Attributes are set via chained builder methods. CSS is built with `Rule`, `Media`, and `Keyframes`, with 400+ typed property methods generated from W3C specs:

```python
Style(
    Rule("body").margin("0").font_family("system-ui, sans-serif"),
    Rule(".container").display("flex").gap("1rem").padding("2rem"),
    Media("max-width: 768px",
        Rule(".container").flex_direction("column"),
    ),
)
```

The built-in server handles routing, sessions, SSE, and WebSockets:

```python
from ztml import *
from ztml.scripts import HTMX
from ztml.server import rt, serve

@rt('/')
def get():
    return Html(
        Head(Title("Counter"), HTMX),
        Body(
            H1("Counter"),
            P("0").id("count"),
            Button("Increment").hx_post("/increment").hx_target("#count"),
        ),
    )

count = 0

@rt('/increment')
def post():
    global count
    count += 1
    return P(str(count)).id("count")

serve()  # localhost:5001
```

See the [docs](https://bleemesser.github.io/ztml/) for the full guide on HTML elements, CSS styling, JavaScript helpers, custom components, and the server layer.

## Examples

```bash
uv run examples/static_page.py > page.html
uv run examples/counter_server.py
uv run examples/todo_server.py
uv run examples/auth_app.py
uv run examples/ws_chat.py
uv run examples/sse_clock.py
```

## Benchmarks

Compared against [FastHTML](https://fastht.ml/) building and rendering nested HTML element trees:

```
Scenario         Library      Elements   Build (ms)   Render (ms)   Total (ms)
---------------------------------------------------------------------------
10x50            ztml             1040         1.44          0.09         1.54
10x50            fasthtml         1040        14.72          2.62        17.35
                             speedup: build 10.2x, render 28.5x, total 11.3x

50x100           ztml            10200        14.65          0.90        15.55
50x100           fasthtml        10200       151.36         26.12       177.61
                             speedup: build 10.3x, render 28.9x, total 11.4x

100x200          ztml            40400        58.04          3.63        61.69
100x200          fasthtml        40400       710.79        106.00       816.57
                             speedup: build 12.2x, render 29.2x, total 13.2x
```
^ `benchmarks/bench.py` (M3 Pro MacBook Pro)

## Building from source

Prerequisites: [Rust toolchain](https://rustup.rs/), Python 3.12+, [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run maturin develop
cargo run --bin gen_stubs --no-default-features  # regenerate .pyi stubs
```

## Running tests

```bash
uv run python -m pytest
cargo test -p ztml-core
```

## Releasing

Bump the version in `crates/ztml-core/Cargo.toml` and `crates/ztml-python/Cargo.toml`, make sure stubs are up to date, then:

```bash
git add -A && git commit -m "bump version to 0.x.y"
git tag v0.x.y
git push && git push origin v0.x.y
```

The `v*` tag triggers the full build matrix (Linux, macOS, Windows) and publishes to PyPI.

## License

[MIT](LICENSE)
