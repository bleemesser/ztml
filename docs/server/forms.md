# Forms and Uploads

## Form data

Name a parameter `form_data` and ztml will parse the request body and inject it automatically. No manual request parsing needed.

```python
from ztml import *
from ztml.server import rt, serve

@rt("/submit", methods=["POST"])
async def post(form_data):
    name = form_data["name"]
    return Div(f"Hello, {name}")
```

On the HTML side, a standard form pointing at the route works:

```python
Form(
    Input().type("text").name("name").placeholder("Your name"),
    Button("Submit"),
).action("/submit").method("post")
```

Or with HTMX, skip the full form and post directly:

```python
Button("Submit").hx_post("/submit").hx_target("#result")
```

## File uploads

Name a parameter `files` to receive uploaded files. These are Starlette `UploadFile` objects.

```python
@rt("/upload", methods=["POST"])
async def post(files):
    upload = files["doc"]
    content = (await upload.read()).decode()
    return Div(f"Got: {content}")
```

You can use both `form_data` and `files` in the same handler if you need to accept a mix of fields and file uploads.

## How it works

The injection is based on parameter names, not type annotations. ztml inspects your function signature and wires up the right values from the request. The recognized names are `form_data`, `files`, `request`, `session`, and any path parameters from the route pattern.
