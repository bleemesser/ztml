"""Tests for the ZTML server (ZTMLApp, routing, HTMX injection)."""

import dataclasses
import pytest
from starlette.testclient import TestClient
from starlette.responses import Response, JSONResponse, RedirectResponse

from ztml import Div, Html, Head, Body, Title, P, Fragment
from ztml.server import ZTMLApp, _inject_head, EventStream


class TestHeadInjection:
    def test_injects_into_full_html(self):
        html = "<html><head></head><body></body></html>"
        result = _inject_head(html)
        assert "htmx.org" in result

    def test_injects_after_opening_head(self):
        html = "<html><head><title>T</title></head><body></body></html>"
        result = _inject_head(html)
        assert result.index("htmx.org") > result.index("<head>")
        assert result.index("htmx.org") < result.index("<title>")

    def test_no_inject_for_fragment(self):
        html = "<div>partial</div>"
        result = _inject_head(html)
        assert "htmx.org" not in result

    def test_no_double_inject(self):
        html = '<html><head><script src="https://unpkg.com/htmx.org"></script></head><body></body></html>'
        result = _inject_head(html)
        assert result.count("htmx.org") == 1

    def test_doctype_triggers_injection(self):
        html = "<!DOCTYPE html><html><head></head><body></body></html>"
        result = _inject_head(html)
        assert "htmx.org" in result

    def test_case_insensitive_html_tag(self):
        html = "<HTML><HEAD></HEAD><BODY></BODY></HTML>"
        result = _inject_head(html)
        assert "htmx.org" in result

    def test_dev_mode_injects_reload_script(self):
        html = "<html><head></head><body></body></html>"
        result = _inject_head(html, dev=True)
        assert "/_ztml/reload" in result
        assert "htmx.org" in result

    def test_no_reload_script_without_dev(self):
        html = "<html><head></head><body></body></html>"
        result = _inject_head(html, dev=False)
        assert "/_ztml/reload" not in result

    def test_no_reload_script_for_fragment(self):
        html = "<div>partial</div>"
        result = _inject_head(html, dev=True)
        assert "/_ztml/reload" not in result


class TestZTMLApp:
    def setup_method(self):
        self.app = ZTMLApp()

    def test_basic_get_route(self):
        @self.app.route("/")
        def get():
            return Div("hello")

        client = TestClient(self.app)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "<div>hello</div>" in resp.text

    def test_route_returns_element(self):
        @self.app.route("/page")
        def get():
            return P("content")

        client = TestClient(self.app)
        resp = client.get("/page")
        assert "<p>content</p>" in resp.text

    def test_route_returns_string(self):
        @self.app.route("/raw")
        def get():
            return "<b>raw</b>"

        client = TestClient(self.app)
        resp = client.get("/raw")
        assert "<b>raw</b>" in resp.text

    def test_route_returns_tuple(self):
        @self.app.route("/multi")
        def get():
            return (Div("a"), Div("b"))

        client = TestClient(self.app)
        resp = client.get("/multi")
        assert "<div>a</div>" in resp.text
        assert "<div>b</div>" in resp.text

    def test_route_returns_response(self):
        @self.app.route("/json")
        def get():
            return JSONResponse({"ok": True})

        client = TestClient(self.app)
        resp = client.get("/json")
        assert resp.json() == {"ok": True}

    def test_explicit_methods(self):
        @self.app.route("/submit", methods=["POST"])
        def submit():
            return Div("submitted")

        client = TestClient(self.app)
        resp = client.post("/submit")
        assert resp.status_code == 200
        assert "submitted" in resp.text

    def test_method_inferred_from_name(self):
        @self.app.route("/data")
        def post():
            return Div("posted")

        client = TestClient(self.app)
        resp = client.post("/data")
        assert resp.status_code == 200

    def test_path_params(self):
        @self.app.route("/items/{item_id}")
        def get(item_id):
            return Div(f"Item: {item_id}")

        client = TestClient(self.app)
        resp = client.get("/items/42")
        assert "Item: 42" in resp.text

    def test_request_param(self):
        @self.app.route("/echo")
        def get(request):
            return Div(str(request.url))

        client = TestClient(self.app)
        resp = client.get("/echo")
        assert "echo" in resp.text

    def test_async_handler(self):
        @self.app.route("/async")
        async def get():
            return Div("async result")

        client = TestClient(self.app)
        resp = client.get("/async")
        assert "async result" in resp.text

    def test_htmx_injected_for_full_page(self):
        @self.app.route("/")
        def get():
            return Html(Head(Title("T")), Body(Div("hi")))

        client = TestClient(self.app)
        resp = client.get("/")
        assert "htmx.org" in resp.text

    def test_htmx_not_injected_for_fragment(self):
        @self.app.route("/partial")
        def get():
            return Div("partial")

        client = TestClient(self.app)
        resp = client.get("/partial")
        assert "htmx.org" not in resp.text

    def test_fragment_rendering(self):
        @self.app.route("/frag")
        def get():
            return Fragment(P("a"), P("b"))

        client = TestClient(self.app)
        resp = client.get("/frag")
        assert "<p>a</p>" in resp.text
        assert "<p>b</p>" in resp.text

    def test_404_for_unknown_route(self):
        @self.app.route("/")
        def get():
            return Div("home")

        client = TestClient(self.app, raise_server_exceptions=False)
        resp = client.get("/nonexistent")
        assert resp.status_code == 404

    def test_method_not_allowed(self):
        @self.app.route("/only-get")
        def get():
            return Div("ok")

        client = TestClient(self.app, raise_server_exceptions=False)
        resp = client.post("/only-get")
        assert resp.status_code == 405

    def test_multiple_routes(self):
        @self.app.route("/a")
        def route_a():
            return Div("A")

        @self.app.route("/b")
        def route_b():
            return Div("B")

        client = TestClient(self.app)
        assert "A" in client.get("/a").text
        assert "B" in client.get("/b").text


class TestFormData:
    def setup_method(self):
        self.app = ZTMLApp()

    def test_form_data_injection(self):
        @self.app.route("/submit", methods=["POST"])
        async def post(form_data):
            name = form_data["name"]
            return Div(f"Hello {name}")

        client = TestClient(self.app)
        resp = client.post("/submit", data={"name": "Alice"})
        assert "Hello Alice" in resp.text

    def test_form_data_multiple_fields(self):
        @self.app.route("/form", methods=["POST"])
        async def post(form_data):
            return Div(f"{form_data['first']} {form_data['last']}")

        client = TestClient(self.app)
        resp = client.post("/form", data={"first": "Jane", "last": "Doe"})
        assert "Jane Doe" in resp.text

    def test_files_injection(self):
        @self.app.route("/upload", methods=["POST"])
        async def post(files):
            upload = files["doc"]
            content = (await upload.read()).decode()
            return Div(f"Got: {content}")

        client = TestClient(self.app)
        resp = client.post("/upload", files={"doc": ("test.txt", b"hello file")})
        assert "Got: hello file" in resp.text

    def test_form_data_and_files_together(self):
        @self.app.route("/both", methods=["POST"])
        async def post(form_data, files):
            name = form_data["name"]
            doc = files["doc"]
            content = (await doc.read()).decode()
            return Div(f"{name}: {content}")

        client = TestClient(self.app)
        resp = client.post(
            "/both",
            data={"name": "Bob"},
            files={"doc": ("f.txt", b"data")},
        )
        assert "Bob: data" in resp.text


class TestSessions:
    def setup_method(self):
        self.app = ZTMLApp(session_secret="test-secret-key")

    def test_session_read_write(self):
        @self.app.route("/set", methods=["POST"])
        def post(session):
            session["user"] = "alice"
            return Div("set")

        @self.app.route("/get")
        def get(session):
            return Div(f"user={session.get('user', 'none')}")

        client = TestClient(self.app)
        client.post("/set")
        resp = client.get("/get")
        assert "user=alice" in resp.text

    def test_session_persists_across_requests(self):
        @self.app.route("/inc", methods=["POST"])
        def post(session):
            session["count"] = session.get("count", 0) + 1
            return Div(f"count={session['count']}")

        client = TestClient(self.app)
        client.post("/inc")
        resp = client.post("/inc")
        assert "count=2" in resp.text

    def test_session_without_secret_raises(self):
        app = ZTMLApp()

        @app.route("/")
        def get(session):
            return Div("no session")

        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/")
        assert resp.status_code == 500


class TestBeforeHooks:
    def setup_method(self):
        self.app = ZTMLApp(session_secret="test-secret")

    def test_before_hook_allows_request(self):
        def check_ok(request):
            return None

        @self.app.route("/", before=[check_ok])
        def get():
            return Div("allowed")

        client = TestClient(self.app)
        resp = client.get("/")
        assert "allowed" in resp.text

    def test_before_hook_redirects(self):
        def require_auth(request):
            return RedirectResponse("/login", status_code=303)

        @self.app.route("/protected", before=[require_auth])
        def get():
            return Div("secret")

        client = TestClient(self.app, follow_redirects=False)
        resp = client.get("/protected")
        assert resp.status_code == 303
        assert "/login" in resp.headers["location"]

    def test_before_hook_accesses_path_params(self):
        def check_id(item_id):
            if item_id == "0":
                return Response("bad id", status_code=400)
            return None

        @self.app.route("/items/{item_id}", before=[check_id])
        def get(item_id):
            return Div(f"Item {item_id}")

        client = TestClient(self.app)
        assert "Item 5" in client.get("/items/5").text

        client2 = TestClient(self.app, raise_server_exceptions=False)
        resp = client2.get("/items/0")
        assert resp.status_code == 400

    def test_multiple_before_hooks(self):
        calls = []

        def hook_a(request):
            calls.append("a")
            return None

        def hook_b(request):
            calls.append("b")
            return None

        @self.app.route("/", before=[hook_a, hook_b])
        def get():
            return Div("ok")

        client = TestClient(self.app)
        client.get("/")
        assert calls == ["a", "b"]

    def test_before_hook_short_circuits(self):
        calls = []

        def hook_a(request):
            calls.append("a")
            return Response("blocked", status_code=403)

        def hook_b(request):
            calls.append("b")
            return None

        @self.app.route("/", before=[hook_a, hook_b])
        def get():
            calls.append("handler")
            return Div("ok")

        client = TestClient(self.app, raise_server_exceptions=False)
        resp = client.get("/")
        assert resp.status_code == 403
        assert calls == ["a"]

    def test_async_before_hook(self):
        async def async_check(request):
            return None

        @self.app.route("/", before=[async_check])
        async def get():
            return Div("ok")

        client = TestClient(self.app)
        assert "ok" in client.get("/").text

    def test_before_hook_with_session(self):
        @self.app.route("/login", methods=["POST"])
        def login(session):
            session["authed"] = True
            return Div("logged in")

        def require_auth(session):
            if not session.get("authed"):
                return RedirectResponse("/login", status_code=303)
            return None

        @self.app.route("/dashboard", before=[require_auth])
        def dashboard():
            return Div("dashboard")

        client = TestClient(self.app, follow_redirects=False)
        resp = client.get("/dashboard")
        assert resp.status_code == 303

        client.post("/login")
        resp = client.get("/dashboard")
        assert "dashboard" in resp.text


class TestLiveReload:
    def test_dev_mode_injects_reload_into_page(self):
        app = ZTMLApp(dev=True)

        @app.route("/")
        def get():
            return Html(Head(Title("T")), Body(Div("hi")))

        client = TestClient(app)
        resp = client.get("/")
        assert "/_ztml/reload" in resp.text

    def test_non_dev_no_reload_script(self):
        app = ZTMLApp(dev=False)

        @app.route("/")
        def get():
            return Html(Head(Title("T")), Body(Div("hi")))

        client = TestClient(app)
        resp = client.get("/")
        assert "/_ztml/reload" not in resp.text

    def test_dev_mode_reload_websocket_endpoint(self):
        app = ZTMLApp(dev=True)

        @app.route("/")
        def get():
            return Div("hi")

        client = TestClient(app)
        with client.websocket_connect("/_ztml/reload"):
            pass  # connection opens successfully


class TestWebSocket:
    def test_ws_decorator(self):
        app = ZTMLApp()

        @app.ws("/echo")
        async def echo(websocket):
            await websocket.accept()
            data = await websocket.receive_text()
            await websocket.send_text(f"echo: {data}")
            await websocket.close()

        client = TestClient(app)
        with client.websocket_connect("/echo") as ws:
            ws.send_text("hello")
            assert ws.receive_text() == "echo: hello"

    def test_ws_with_path_params(self):
        app = ZTMLApp()

        @app.ws("/chat/{room}")
        async def chat(websocket, room):
            await websocket.accept()
            await websocket.send_text(f"room: {room}")
            await websocket.close()

        client = TestClient(app)
        with client.websocket_connect("/chat/lobby") as ws:
            assert ws.receive_text() == "room: lobby"


class TestSSE:
    def test_event_stream(self):
        app = ZTMLApp()

        async def gen():
            yield Div("one")
            yield Div("two")

        @app.route("/stream")
        async def get():
            return EventStream(gen()).response()

        client = TestClient(app)
        resp = client.get("/stream")
        assert resp.headers["content-type"].startswith("text/event-stream")
        assert "data: <div>one</div>" in resp.text
        assert "data: <div>two</div>" in resp.text


class TestDataclassIntegration:
    def setup_method(self):
        self.app = ZTMLApp()

    def test_dataclass_with_ztml_render(self):
        @dataclasses.dataclass
        class User:
            name: str
            age: int

            def __ztml_render__(self):
                return Div(f"{self.name}, {self.age}")

        @self.app.route("/user")
        def get():
            return User(name="Alice", age=30)

        client = TestClient(self.app)
        resp = client.get("/user")
        assert "Alice, 30" in resp.text


