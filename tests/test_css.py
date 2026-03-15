"""Tests for CSS rule building, keyframes, media queries, and style rendering."""

from ztml import render, Style, Rule, Media, Keyframes, Frame, RawCss, InlineStyle, Div

class TestRule:
    def test_basic_rule(self):
        html = render(Style(Rule("body").color("red")))
        assert "body" in html
        assert "color" in html
        assert "red" in html

    def test_multiple_properties(self):
        html = render(Style(
            Rule(".box").color("blue").margin("10px").padding("5px")
        ))
        assert "color" in html
        assert "margin" in html
        assert "padding" in html

    def test_chaining_returns_rule(self):
        r = Rule(".x").color("red")
        r2 = r.font_size("16px")
        # chaining should return the same or a new Rule
        assert r2 is not None

    def test_prop_custom_property(self):
        html = render(Style(Rule(".card").prop("box-shadow", "0 2px 4px black")))
        assert "box-shadow" in html
        assert "0 2px 4px black" in html

    def test_complex_selector(self):
        html = render(Style(Rule(".parent > .child:hover").color("green")))
        assert ".parent > .child:hover" in html

    def test_multiple_rules(self):
        html = render(Style(
            Rule("h1").font_size("2rem"),
            Rule("h2").font_size("1.5rem"),
        ))
        assert "h1" in html
        assert "h2" in html

    def test_layout_properties(self):
        html = render(Style(
            Rule(".flex").display("flex").justify_content("center").align_items("center")
        ))
        assert "display" in html
        assert "flex" in html
        assert "justify-content" in html
        assert "align-items" in html

    def test_border_properties(self):
        html = render(Style(
            Rule(".bordered").border("1px solid black").border_radius("8px")
        ))
        assert "border" in html
        assert "border-radius" in html

    def test_position_properties(self):
        html = render(Style(
            Rule(".abs").position("absolute").top("0").left("0")
        ))
        assert "position" in html
        assert "absolute" in html

class TestKeyframes:
    def test_basic_keyframes(self):
        html = render(Style(
            Keyframes("fadeIn",
                Frame("from").opacity("0"),
                Frame("to").opacity("1"),
            )
        ))
        assert "@keyframes" in html
        assert "fadeIn" in html
        assert "opacity" in html

    def test_percentage_frame(self):
        html = render(Style(
            Keyframes("slide",
                Frame("0%").transform("translateX(0)"),
                Frame("50%").transform("translateX(50px)"),
                Frame("100%").transform("translateX(100px)"),
            )
        ))
        assert "50%" in html
        assert "transform" in html

    def test_frame_multiple_props(self):
        html = render(Style(
            Keyframes("anim",
                Frame("from").opacity("0").transform("scale(0.5)"),
                Frame("to").opacity("1").transform("scale(1)"),
            )
        ))
        assert "opacity" in html
        assert "transform" in html

    def test_frame_custom_prop(self):
        html = render(Style(
            Keyframes("custom",
                Frame("0%").prop("--my-var", "0"),
                Frame("100%").prop("--my-var", "1"),
            )
        ))
        assert "--my-var" in html

class TestMedia:
    def test_basic_media(self):
        html = render(Style(
            Media("(max-width: 768px)",
                Rule(".container").padding("1rem"),
            )
        ))
        assert "@media" in html
        assert "(max-width: 768px)" in html
        assert ".container" in html

    def test_media_multiple_rules(self):
        html = render(Style(
            Media("(prefers-color-scheme: dark)",
                Rule("body").background_color("#111").color("#eee"),
                Rule("a").color("#88f"),
            )
        ))
        assert "@media" in html
        assert "body" in html
        assert "a" in html

class TestRawCss:
    def test_raw_css_in_style(self):
        html = render(Style(
            RawCss("* { box-sizing: border-box; }")
        ))
        assert "* { box-sizing: border-box; }" in html

    def test_raw_css_mixed_with_rules(self):
        html = render(Style(
            RawCss("@import url('fonts.css');"),
            Rule("body").font_family("sans-serif"),
        ))
        assert "@import" in html
        assert "body" in html

class TestStyleTag:
    def test_style_wraps_in_tag(self):
        html = render(Style(Rule("p").color("black")))
        assert html.startswith("<style>")
        assert html.endswith("</style>")

    def test_empty_style(self):
        html = render(Style())
        assert "<style>" in html

class TestInlineStyle:
    def test_inline_style_basic(self):
        s = InlineStyle().color("red").font_size("16px")
        assert s is not None

    def test_inline_style_on_element(self):
        html = render(Div("styled").style(InlineStyle().color("red").font_weight("bold")))
        assert 'style="color: red; font-weight: bold"' in html
