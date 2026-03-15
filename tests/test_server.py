"""Tests for the ZTML server (ZTMLApp, routing, HTMX injection)."""

import pytest
from starlette.testclient import TestClient
from starlette.responses import Response, JSONResponse

from ztml import render, Div, Html, Head, Body, Title, P, Fragment
from ztml.server import ZTMLApp, _inject_htmx

class TestHtmxInjection:
    def test_injects_into_full_html(self):
        html = "<html><head></head><body></body></html>"
        result = _inject_htmx(html)
        assert "htmx.org" in result

    def test_injects_before_closing_head(self):
        html = "<html><head><title>T</title></head><body></body></html>"
        result = _inject_htmx(html)
        assert result.index("htmx.org") < result.index("</head>")

    def test_no_inject_for_fragment(self):
        html = "<div>partial</div>"
        result = _inject_htmx(html)
        assert "htmx.org" not in result

    def test_no_double_inject(self):
        html = '<html><head><script src="https://unpkg.com/htmx.org"></script></head><body></body></html>'
        result = _inject_htmx(html)
        assert result.count("htmx.org") == 1

    def test_doctype_triggers_injection(self):
        html = "<!DOCTYPE html><html><head></head><body></body></html>"
        result = _inject_htmx(html)
        assert "htmx.org" in result

    def test_case_insensitive_html_tag(self):
        html = "<HTML><HEAD></HEAD><BODY></BODY></HTML>"
        result = _inject_htmx(html)
        assert "htmx.org" in result


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
