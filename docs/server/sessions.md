# Sessions and Auth

## Sessions

Pass `session_secret` to `ZTMLApp` to enable cookie-backed sessions. Then name a parameter `session` in any handler to get a dict-like session object.

```python
from ztml import *
from ztml.server import ZTMLApp, serve

app = ZTMLApp(session_secret="your-secret-key")

@app.route("/login", methods=["POST"])
def login(session, form_data):
    session["user"] = form_data["username"]
    return Div("Logged in")

@app.route("/profile")
def profile(session):
    return Div(f"Hello, {session.get('user', 'guest')}")

serve(target=app)
```

Sessions are backed by Starlette's `SessionMiddleware`, which stores data in signed cookies. This is simple and stateless, no database or Redis needed, but it means session data should be kept small.

## Before hooks

Before hooks run checks before a route handler executes. They're useful for auth guards, logging, or any cross-cutting concern. If a hook returns a `Response`, it short-circuits the handler.

```python
from starlette.responses import RedirectResponse

def require_auth(session):
    if not session.get("user"):
        return RedirectResponse("/login", status_code=303)

@app.route("/dashboard", before=[require_auth])
def dashboard(session):
    return Div(f"Welcome, {session['user']}")
```

Hooks use the same parameter injection as routes. You can ask for `session`, `request`, path parameters, or `form_data` and they'll be wired up.

Multiple hooks run in order. The first one to return a `Response` wins and the rest (including the handler) are skipped.

```python
@app.route("/admin", before=[require_auth, require_admin_role])
def admin_panel(session):
    return Div("Admin stuff")
```

Hooks can be sync or async.

## Raw cookies

For cookies outside of sessions, use Starlette's built-in methods directly via the `request` object:

```python
@app.route("/set-pref", methods=["POST"])
def set_pref(request):
    theme = request.cookies.get("theme", "light")
    # ...
```

To set cookies, return a Starlette `Response` and call `response.set_cookie()` on it.
