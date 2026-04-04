# Routing

> NOTE: Server features require the `serve` extra: `pip install ztml[serve]`

ztml includes a built-in server layer on top of Starlette and Uvicorn. It's intentionally thin, enough for internal tools, dashboards, and prototypes without pulling in a full framework. If you're looking to write a larger web app, you can use ztml's components to define the UI and bring your own server instead, though you may need to manually call `render()`.

## Basic routes

The simplest setup uses the module-level `rt` decorator and `serve` function.

```python
from ztml import *
from ztml.scripts import HTMX
from ztml.server import rt, serve

@rt("/")
def get():
    return Html(
        Head(Title("Hello"), HTMX),
        Body(H1("It works")),
    )

serve()  # localhost:5001
```

The HTTP method is inferred from the function name. A function named `get` handles GET requests, `post` handles POST, and so on. If the name doesn't match a standard method, it defaults to GET.

You might prefer to be explicit with the methods, especially if you want to define multiple endpoints that have the same protocol without name shadowing.

```python
@rt("/submit", methods=["POST"])
def handle_submit():
    return Div("submitted")
```

## ZTMLApp
By default, `ztml.server` always provides an app instance. For more control, create your own `ZTMLApp`. This is what you'll use when you need sessions, multiple route groups, hot reload, or want to pass the app around.

```python
from ztml.server import ZTMLApp, serve

app = ZTMLApp()

@app.route("/")
def get():
    return Div("hello")

serve(target=app)
```

## Path parameters

Path parameters are extracted from the URL and passed as function arguments.

```python
@app.route("/users/{user_id}")
def get(user_id):
    return Div(f"User: {user_id}")
```

## Request access

Name a parameter `request` to get the full Starlette `Request` object.

```python
@app.route("/debug")
def get(request):
    return Div(f"URL: {request.url}")
```

## Returning responses

Route handlers can return ztml elements (rendered automatically), tuples of elements (concatenated), plain strings, or Starlette `Response` objects for full control.

```python
from starlette.responses import RedirectResponse

@app.route("/old-page")
def get():
    return RedirectResponse("/new-page", status_code=301)
```

## Live reload

Set `dev=True` to enable file-watching and automatic browser refresh on save. Uvicorn handles the file watching, and ztml injects a small WebSocket script that triggers a reload when the server restarts. 

```python
app = ZTMLApp(dev=True)
```

Sometimes, uvicorn doesn't like it when you enable hot reload on a script not in the current directory and will not launch. I think I've fixed this issue, but please report it if it happens to you. In the meantime, disable dev mode or `cd` into the same directory as the script you're trying to run.