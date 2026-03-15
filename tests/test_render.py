"""Tests for the render function edge cases and error paths."""

import pytest
from ztml import render, Div, Fragment, Style, Script, Rule

class TestRenderErrors:
    def test_render_none_raises(self):
        with pytest.raises((TypeError, Exception)):
            render(None)

    def test_render_int_raises(self):
        with pytest.raises((TypeError, Exception)):
            render(42)

    def test_render_list_raises(self):
        with pytest.raises((TypeError, Exception)):
            render([Div("a")])

    def test_render_dict_raises(self):
        with pytest.raises((TypeError, Exception)):
            render({"key": "value"})

    def test_render_plain_object_without_protocol_raises(self):
        class Foo:
            pass
        with pytest.raises((TypeError, Exception)):
            render(Foo())

class TestRenderValid:
    def test_render_element(self):
        html = render(Div("test"))
        assert "<div>test</div>" == html

    def test_render_fragment(self):
        html = render(Fragment(Div("a")))
        assert "<div>a</div>" == html

    def test_render_style(self):
        html = render(Style(Rule("p").color("red")))
        assert "<style>" in html

    def test_render_script(self):
        html = render(Script())
        assert "<script>" in html

    def test_render_custom_protocol(self):
        class Widget:
            def __ztml_render__(self):
                return Div("widget")

        assert "<div>widget</div>" in render(Widget())

class TestChildrenTypes:
    def test_string_child(self):
        assert render(Div("text")) == "<div>text</div>"

    def test_int_child(self):
        html = render(Div(42))
        assert "42" in html

    def test_float_child(self):
        html = render(Div(3.14))
        assert "3.14" in html

    def test_bool_child(self):
        html = render(Div(True))
        assert "true" in html.lower() or "True" in html

    def test_element_child(self):
        html = render(Div(Div("inner")))
        assert "<div><div>inner</div></div>" == html

    def test_deeply_nested(self):
        html = render(Div(Div(Div(Div("deep")))))
        assert "<div><div><div><div>deep</div></div></div></div>" == html

    def test_many_children(self):
        children = [Div(str(i)) for i in range(20)]
        html = render(Div(*children))
        for i in range(20):
            assert f"<div>{i}</div>" in html

    def test_mixed_children_types(self):
        html = render(Div("text", Div("nested"), 42))
        assert "text" in html
        assert "<div>nested</div>" in html
        assert "42" in html
