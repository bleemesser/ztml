# JavaScript

## Event handlers

The `On` helper generates event listener boilerplate. Pass a CSS selector and the handler body.

```python
from ztml import *

Script(
    On.click("#increment", """
        let count = document.getElementById('count');
        count.textContent = parseInt(count.textContent) + 1;
    """),
)
```

This renders a `<script>` block with a `document.querySelector` and `addEventListener` call. Nothing fancy, it's just saving you the boilerplate.

Available helpers: `On.click`, `On.submit`, `On.change`, `On.input`, `On.keydown`, `On.keyup`, `On.mouseover`, `On.mouseout`, `On.focus`, `On.blur`, `On.document_ready`, and `On.event` for anything else.

## Raw JavaScript

`RawJs` injects arbitrary JavaScript into a `Script` block. Use it for function definitions, library initialization, or anything that doesn't fit the event handler pattern.

```python
Script(
    RawJs("function greet(name) { alert('Hello, ' + name); }"),
    On.click("#greet-btn", "greet('world')"),
)
```

## Mixing handlers

A single `Script()` block can contain any combination of `On` handlers and `RawJs` fragments. They're concatenated in order.

```python
Script(
    RawJs("""
        const ws = new WebSocket("ws://" + location.host + "/ws");
        const messages = document.getElementById("messages");

        ws.onmessage = function(e) {
            const div = document.createElement("div");
            div.innerHTML = e.data;
            messages.appendChild(div);
        };

        function sendMsg() {
            const input = document.getElementById("msg");
            if (input.value.trim()) {
                ws.send(input.value.trim());
                input.value = "";
            }
        }
    """),
    On.click("#send", "sendMsg()"),
    On.keydown("#msg", 'if (event.key === "Enter") sendMsg();'),
)
```

If you're using HTMX, you shouldn't need to write much JavaScript at all. The `hx_*` attribute methods on elements handle most interactions declaratively.
