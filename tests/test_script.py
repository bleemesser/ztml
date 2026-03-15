"""Tests for Script, EventHandler (On), and RawJs."""

import pytest
from ztml import render, Script, On, RawJs, EventHandler

class TestScript:
    def test_empty_script(self):
        html = render(Script())
        assert "<script>" in html
        assert "</script>" in html

    def test_script_src(self):
        html = render(Script().src("https://example.com/app.js"))
        assert 'src="https://example.com/app.js"' in html

    def test_script_defer(self):
        html = render(Script().src("/app.js").defer())
        assert "defer" in html

    def test_script_async(self):
        html = render(Script().src("/app.js").async_())
        assert "async" in html

    def test_script_type(self):
        html = render(Script().type("module"))
        assert 'type="module"' in html

    def test_script_crossorigin(self):
        html = render(Script().src("/x.js").crossorigin("anonymous"))
        assert 'crossorigin="anonymous"' in html

    def test_script_integrity(self):
        html = render(Script().src("/x.js").integrity("sha384-abc"))
        assert 'integrity="sha384-abc"' in html

    def test_script_with_raw_js(self):
        html = render(Script(RawJs("console.log('hi')")))
        assert "console.log('hi')" in html

    def test_script_chained_attrs(self):
        html = render(Script().src("/x.js").defer().type("module").crossorigin("anonymous"))
        assert 'src="/x.js"' in html
        assert "defer" in html
        assert 'type="module"' in html

class TestOnEvents:
    def test_on_click(self):
        handler = On.click("#btn", "alert('clicked')")
        assert isinstance(handler, EventHandler)
        html = render(Script(handler))
        assert "click" in html
        assert "alert('clicked')" in html

    def test_on_submit(self):
        html = render(Script(On.submit("form", "event.preventDefault()")))
        assert "submit" in html

    def test_on_change(self):
        html = render(Script(On.change("#select", "update()")))
        assert "change" in html

    def test_on_input(self):
        html = render(Script(On.input("#search", "filter()")))
        assert "input" in html

    def test_on_keydown(self):
        html = render(Script(On.keydown("body", "handleKey(event)")))
        assert "keydown" in html

    def test_on_keyup(self):
        html = render(Script(On.keyup("#field", "validate()")))
        assert "keyup" in html

    def test_on_mouseover(self):
        html = render(Script(On.mouseover(".card", "highlight(this)")))
        assert "mouseover" in html

    def test_on_mouseout(self):
        html = render(Script(On.mouseout(".card", "unhighlight(this)")))
        assert "mouseout" in html

    def test_on_focus(self):
        html = render(Script(On.focus("#input", "expand()")))
        assert "focus" in html

    def test_on_blur(self):
        html = render(Script(On.blur("#input", "collapse()")))
        assert "blur" in html

    def test_on_document_ready(self):
        html = render(Script(On.document_ready("init()")))
        assert "DOMContentLoaded" in html or "init()" in html

    def test_multiple_handlers(self):
        html = render(Script(
            On.click("#a", "doA()"),
            On.click("#b", "doB()"),
        ))
        assert "doA()" in html
        assert "doB()" in html

class TestRawJs:
    def test_raw_js_verbatim(self):
        js = "const x = 1 + 2;"
        html = render(Script(RawJs(js)))
        assert js in html

    def test_raw_js_mixed_with_handlers(self):
        html = render(Script(
            RawJs("let count = 0;"),
            On.click("#inc", "count++"),
        ))
        assert "let count = 0;" in html
        assert "count++" in html
