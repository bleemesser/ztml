# ztml

A Rust-backed framework for building websites in pure Python. ZTML allows you to define HTML/CSS/JS using only Python expressions with as much autocompletion support as I could reasonably add. Inspired by [FastHTML](https://fastht.ml/).

## Install

```bash
pip install ztml
```

## HTML

Every HTML element has a corresponding constructor function. Attributes are set via chained builder methods. Call `render()` to get an HTML string.

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

Attributes chain naturally:

```python
Div(
    Input().type("text").name("q").placeholder("Search...").autofocus(),
    Button("Go").type("submit"),
).cls("search-box").id("search")
```

Use `Fragment` to group elements without a wrapper tag, and `Raw` to inject unescaped HTML:

```python
Fragment(
    H1("Title"),
    P("Paragraph"),
    Raw("<hr/>"),
)
```

## Style

Build CSS with `Rule`, `Media`, `Keyframes`, and `Frame`. Wrap them in `Style()` to render a `<style>` block.

```python
Style(
    Rule("body").margin("0").font_family("system-ui, sans-serif"),
    Rule(".container").display("flex").gap("1rem").padding("2rem"),
    Rule(".container > .sidebar").width("250px").flex_shrink("0"),
    Rule(".container > .main").flex("1"),

    Media("max-width: 768px",
        Rule(".container").flex_direction("column"),
        Rule(".container > .sidebar").width("100%"),
    ),

    Keyframes("fadeIn",
        Frame("from").opacity("0").transform("translateY(-10px)"),
        Frame("to").opacity("1").transform("translateY(0)"),
    ),

    Rule(".card").animation("fadeIn 0.3s ease-out"),
)
```

CSS property methods are generated from W3C specs — every standard property is available with autocompletion. Use `.prop("custom-property", "value")` for anything not covered.

Inline styles work too:

```python
Div("styled").style(InlineStyle().color("red").font_weight("bold"))
```

## Script

Build JavaScript with `On` event handlers and `RawJs`. Wrap them in `Script()` to render a `<script>` block.

```python
Script(
    On.click("#increment", """
        let count = document.getElementById('count');
        count.textContent = parseInt(count.textContent) + 1;
    """),

    On.document_ready("console.log('page loaded')"),

    On.submit("#my-form", """
        event.preventDefault();
        alert('submitted!');
    """),

    RawJs("function greet(name) { alert('Hello, ' + name); }"),
)
```

Available event helpers: `On.click`, `On.submit`, `On.change`, `On.input`, `On.keydown`, `On.keyup`, `On.mouseover`, `On.mouseout`, `On.focus`, `On.blur`, `On.document_ready`, and `On.event` for custom events.

## Custom Components

Any Python object with a `__ztml_render__` method can be used as a renderable component. The method should return a ztml element.

```python
class Card:
    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __ztml_render__(self):
        return Div(
            H2(self.title),
            P(self.body),
        ).cls("card")

# Use directly in render()
print(render(Card("Hello", "World")))

# Or nest inside other elements
page = Div(
    Card("First", "Some content"),
    Card("Second", "More content"),
).cls("cards")
```

## Putting It Together

A complete page with HTML, CSS, and JS:

```python
from ztml import *

def page():
    return Html(
        Head(
            Meta().charset("utf-8"),
            Title("Counter"),
            Style(
                Rule("body").font_family("system-ui").display("flex")
                    .justify_content("center").padding("4rem"),
                Rule("button").padding("0.5rem 1rem").font_size("1.2rem")
                    .cursor("pointer").border_radius("4px"),
                Rule("#count").font_size("3rem").margin("1rem 0"),
            ),
        ),
        Body(
            H1("Counter"),
            P("0").id("count"),
            Button("Increment").id("increment"),
            Script(
                On.click("#increment", """
                    let el = document.getElementById('count');
                    el.textContent = parseInt(el.textContent) + 1;
                """),
            ),
        ),
    )

print(render(page()))
```

## Server

ztml includes a built-in server for HTMX-powered apps, built on Starlette and Uvicorn.

```python
from ztml import *
from ztml.server import rt, serve

@rt('/')
def get():
    return Html(
        Head(Title("Counter")),
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

Key features:
- **Method inference** — the HTTP method is inferred from the function name (`get`, `post`, `put`, `delete`, etc.)
- **Auto HTMX** — full-page responses (`<html>`) get the HTMX script auto-injected
- **Path parameters** — `@rt('/greet/{name}')` extracts `name` as a function argument
- **Request access** — add a `request` parameter to access the Starlette `Request` object
- **Element rendering** — handlers return ztml elements, automatically rendered to HTML

## Building from Source

Prerequisites: [Rust toolchain](https://rustup.rs/), Python 3.12+, [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies and build the Rust extension
uv sync

# For iterative development (faster rebuilds)
uv run maturin develop

# Generate .pyi type stubs for autocompletion
cargo run --bin gen_stubs --no-default-features
```

To build a distributable wheel:

```bash
maturin build --release
# Output in target/wheels/
```

## Examples

```bash
# Generate a static HTML page to stdout 
uv run examples/static_page.py > page.html # (open page.html in your browser!)

# HTMX counter app (localhost:5001)
uv run examples/counter_server.py

# Custom components demo
uv run examples/components.py > components.html

# HTMX todo app (localhost:5001)
uv run examples/todo_server.py
```

## Running Tests

```bash
uv run python -m pytest

# Rust unit tests
cargo test -p ztml-core
```

### How codegen works

`build.rs` reads HTML element definitions from [webtags](https://webtags.nonstrict.eu/) and CSS property specs from [w3c/webref](https://github.com/w3c/webref), stored in `specs/`. From these it generates:

- **Element constructors** — one Python function per HTML tag
- **CSS property methods** — on `Rule`, `InlineStyle`, and `Frame`
- **Enum classes** — for CSS keyword values and HTML attribute values

## License

[MIT](LICENSE)
