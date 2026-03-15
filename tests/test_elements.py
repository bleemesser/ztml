"""Tests for HTML element construction and rendering."""

import pytest
from ztml import (
    render, Div, Span, P, H1, H2, A, Img, Input, Button, Form, Label,
    Ul, Ol, Li, Table, Tr, Th, Td, Thead, Tbody,
    Html, Head, Body, Title, Meta, Link, Script, Style,
    Fragment, Raw, Custom, Br, Hr,
    Select, Option, Textarea, Fieldset, Legend,
    Section, Article, Nav, Header, Footer, Main,
    Details, Summary,
)

class TestBasicElements:
    def test_empty_div(self):
        assert render(Div()) == "<div></div>"

    def test_div_with_text(self):
        assert render(Div("hello")) == "<div>hello</div>"

    def test_nested_elements(self):
        html = render(Div(Span("inner")))
        assert html == "<div><span>inner</span></div>"

    def test_multiple_children(self):
        html = render(Div(Span("a"), Span("b")))
        assert "<span>a</span>" in html
        assert "<span>b</span>" in html

    def test_heading_tags(self):
        assert render(H1("title")) == "<h1>title</h1>"
        assert render(H2("sub")) == "<h2>sub</h2>"

    def test_paragraph(self):
        assert render(P("text")) == "<p>text</p>"

    def test_void_elements(self):
        html = render(Br())
        assert "br" in html
        html = render(Hr())
        assert "hr" in html

    def test_self_closing_input(self):
        html = render(Input())
        assert "input" in html

    def test_semantic_elements(self):
        for el_fn, tag in [
            (Section, "section"), (Article, "article"), (Nav, "nav"),
            (Header, "header"), (Footer, "footer"), (Main, "main"),
        ]:
            assert f"<{tag}>" in render(el_fn()) or f"<{tag}></{tag}>" in render(el_fn())

class TestAttributes:
    def test_id(self):
        html = render(Div().id("main"))
        assert 'id="main"' in html

    def test_cls_single(self):
        html = render(Div().cls("container"))
        assert 'class="container"' in html

    def test_cls_multiple(self):
        html = render(Div().cls("a", "b", "c"))
        assert 'class="a b c"' in html

    def test_style_attr(self):
        html = render(Div().style("color: red"))
        assert 'style="color: red"' in html

    def test_title_attr(self):
        html = render(Div().title("tooltip"))
        assert 'title="tooltip"' in html

    def test_hidden(self):
        html = render(Div().hidden())
        assert "hidden" in html

    def test_tabindex(self):
        html = render(Div().tabindex(0))
        assert 'tabindex="0"' in html

    def test_role(self):
        html = render(Div().role("button"))
        assert 'role="button"' in html

    def test_data_attribute(self):
        html = render(Div().data("id", "42"))
        assert 'data-id="42"' in html

    def test_aria_attribute(self):
        html = render(Div().aria("label", "Close"))
        assert 'aria-label="Close"' in html

    def test_custom_attr(self):
        html = render(Div().attr("x-data", "{}"))
        assert 'x-data="{}"' in html

    def test_chained_attributes(self):
        html = render(Div().id("x").cls("y").role("button"))
        assert 'id="x"' in html
        assert 'class="y"' in html
        assert 'role="button"' in html

class TestLinkMediaAttributes:
    def test_anchor(self):
        html = render(A("click").href("/page").target("_blank"))
        assert 'href="/page"' in html
        assert 'target="_blank"' in html
        assert "click" in html

    def test_img(self):
        html = render(Img().src("/img.png").alt("photo").width("100").height("50"))
        assert 'src="/img.png"' in html
        assert 'alt="photo"' in html
        assert 'width="100"' in html

    def test_loading_lazy(self):
        html = render(Img().loading("lazy"))
        assert 'loading="lazy"' in html

class TestFormAttributes:
    def test_input_type(self):
        html = render(Input().type("email").name("email").placeholder("you@example.com"))
        assert 'type="email"' in html
        assert 'name="email"' in html
        assert 'placeholder="you@example.com"' in html

    def test_required(self):
        html = render(Input().required())
        assert "required" in html

    def test_disabled(self):
        html = render(Input().disabled())
        assert "disabled" in html

    def test_checked(self):
        html = render(Input().type("checkbox").checked())
        assert "checked" in html

    def test_value(self):
        html = render(Input().value("hello"))
        assert 'value="hello"' in html

    def test_form_action_method(self):
        html = render(Form().action("/submit").method("POST"))
        assert 'action="/submit"' in html
        assert 'method="POST"' in html

    def test_textarea_rows_cols(self):
        html = render(Textarea().rows(5).cols(40))
        assert 'rows="5"' in html
        assert 'cols="40"' in html

    def test_label_for(self):
        html = render(Label("Name").html_for("name"))
        assert 'for="name"' in html

    def test_select_with_options(self):
        html = render(Select(
            Option("A").value("a"),
            Option("B").value("b").selected(),
        ))
        assert "<select>" in html or "<select" in html
        assert 'value="a"' in html
        assert "selected" in html

    def test_min_max_pattern(self):
        html = render(Input().type("number").min("0").max("100").pattern("[0-9]+"))
        assert 'min="0"' in html
        assert 'max="100"' in html
        assert 'pattern="[0-9]+"' in html

    def test_multiple(self):
        html = render(Select().multiple())
        assert "multiple" in html

class TestTableAttributes:
    def test_colspan_rowspan(self):
        html = render(Td("cell").colspan(2).rowspan(3))
        assert 'colspan="2"' in html
        assert 'rowspan="3"' in html

    def test_scope(self):
        html = render(Th("Header").scope("col"))
        assert 'scope="col"' in html

    def test_full_table(self):
        html = render(Table(
            Thead(Tr(Th("A"), Th("B"))),
            Tbody(Tr(Td("1"), Td("2"))),
        ))
        assert "<table>" in html or "<table" in html
        assert "<thead>" in html
        assert "<tbody>" in html
        assert "<th>" in html or "<th" in html

class TestHtmxAttributes:
    def test_hx_get(self):
        html = render(Button("Load").hx_get("/data"))
        assert 'hx-get="/data"' in html

    def test_hx_post(self):
        html = render(Button("Submit").hx_post("/submit"))
        assert 'hx-post="/submit"' in html

    def test_hx_target(self):
        html = render(Button("Go").hx_get("/x").hx_target("#result"))
        assert 'hx-target="#result"' in html

    def test_hx_swap(self):
        html = render(Div().hx_swap("outerHTML"))
        assert 'hx-swap="outerHTML"' in html

    def test_hx_trigger(self):
        html = render(Input().hx_get("/search").hx_trigger("keyup changed delay:300ms"))
        assert 'hx-trigger="keyup changed delay:300ms"' in html

    def test_hx_confirm(self):
        html = render(Button("Delete").hx_delete("/item/1").hx_confirm("Sure?"))
        assert 'hx-confirm="Sure?"' in html

    def test_hx_put_patch_delete(self):
        assert 'hx-put="/a"' in render(Div().hx_put("/a"))
        assert 'hx-patch="/b"' in render(Div().hx_patch("/b"))
        assert 'hx-delete="/c"' in render(Div().hx_delete("/c"))

    def test_hx_boost(self):
        html = render(Div().hx_boost())
        assert 'hx-boost="true"' in html

    def test_hx_on(self):
        html = render(Div().hx_on("click", "alert('hi')"))
        assert "hx-on" in html

class TestFragmentAndRaw:
    def test_fragment_no_wrapper(self):
        html = render(Fragment(Span("a"), Span("b")))
        assert html == "<span>a</span><span>b</span>"

    def test_fragment_empty(self):
        assert render(Fragment()) == ""

    def test_raw_html(self):
        html = render(Div(Raw("<b>bold</b>")))
        assert "<b>bold</b>" in html

    def test_raw_not_escaped(self):
        # Raw can't be rendered standalone, only as a child of an element
        html = render(Div(Raw("<b>bold</b>")))
        assert "<b>bold</b>" in html

class TestCustomElement:
    def test_custom_tag(self):
        html = render(Custom("my-widget", "content"))
        assert "<my-widget>" in html
        assert "content" in html
        assert "</my-widget>" in html

    def test_custom_with_attrs(self):
        html = render(Custom("x-component").id("c1").cls("active"))
        assert 'id="c1"' in html
        assert 'class="active"' in html

class TestEscaping:
    def test_text_is_escaped(self):
        html = render(Div("<script>alert(1)</script>"))
        assert "<script>" not in html
        assert "&lt;" in html or "&#" in html

    def test_attribute_is_escaped(self):
        html = render(Div().id('x" onclick="alert(1)'))
        # The attribute value should be escaped, not break out
        assert 'onclick' not in html or '&quot;' in html or "&#" in html

class TestCustomRender:
    def test_ztml_render_protocol(self):
        class MyComponent:
            def __ztml_render__(self):
                return Div("custom")

        html = render(MyComponent())
        assert "<div>custom</div>" in html

class TestInteractiveElements:
    def test_details_summary(self):
        html = render(Details(Summary("Click"), P("Hidden content")))
        assert "<details>" in html or "<details" in html
        assert "<summary>" in html or "<summary" in html

class TestMetaAttributes:
    def test_meta_charset(self):
        html = render(Meta().charset("utf-8"))
        assert 'charset="utf-8"' in html

    def test_meta_content(self):
        html = render(Meta().name("viewport").content("width=device-width"))
        assert 'content="width=device-width"' in html

    def test_meta_http_equiv(self):
        html = render(Meta().http_equiv("refresh").content("5"))
        assert 'http-equiv="refresh"' in html
