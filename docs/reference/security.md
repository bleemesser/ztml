# Security and Escaping

## Auto-escaping

All text content and attribute values are HTML-escaped automatically by the Rust core. Characters like `<`, `>`, `&`, and `"` are converted to their HTML entities before rendering.

```python
# this is safe
Div(user_input)  # <script>alert('xss')</script> becomes &lt;script&gt;...
```

This applies to text passed as children and to values passed to attribute methods. You don't need to think about it for normal usage.

## Raw

`Raw()` is what it sounds like. It injects its content directly into the output with no escaping. This exists for cases where you're constructing trusted HTML yourself: SVG snippets, content from a sanitizer, etc.

```python
Raw("<hr/>")               # fine
Raw(user_comment)          # dangerous
Raw(sanitize(user_comment))  # fine if your sanitizer is trustworthy
```

Never pass user input to `Raw()`. If you're accepting content from users and need to render HTML, run it through a sanitizer first.

## RawJs and Script

`RawJs` injects JavaScript without escaping, since that's kinda the whole point. The same caution applies. Don't interpolate user input into JavaScript strings. Use data attributes or JSON serialization to pass dynamic data to client-side code.

```python
# pls no
Script(RawJs(f"alert('{user_input}')"))

# ok
Div().attr("data-name", user_input).id("target"),
Script(RawJs("alert(document.getElementById('target').dataset.name)"))
```
