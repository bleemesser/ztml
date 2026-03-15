"""Tests for CSS value constant classes."""

from ztml import (
    Display, Position, FlexDirection, FlexWrap, TextAlign,
    AlignItems, AlignContent, JustifyContent, Cursor,
    Overflow, FontWeight, FontStyle, BoxSizing,
    BorderStyle, Visibility,
)

class TestCssConstants:
    def test_display_values(self):
        assert Display.flex == "flex"
        assert Display.block == "block"
        assert Display.inline == "inline"
        assert Display.none == "none"
        assert Display.grid == "grid"

    def test_position_values(self):
        assert Position.absolute == "absolute"
        assert Position.relative == "relative"
        assert Position.fixed == "fixed"
        assert Position.sticky == "sticky"
        assert Position.static_ == "static"

    def test_flex_direction(self):
        assert FlexDirection.row == "row"
        assert FlexDirection.column == "column"

    def test_text_align(self):
        assert TextAlign.center == "center"
        assert TextAlign.left == "left"
        assert TextAlign.right == "right"

    def test_align_items(self):
        assert AlignItems.center == "center"
        assert AlignItems.flex_start == "flex-start"
        assert AlignItems.flex_end == "flex-end"
        assert AlignItems.stretch == "stretch"

    def test_justify_content(self):
        assert JustifyContent.center == "center"
        assert JustifyContent.space_between == "space-between"

    def test_cursor(self):
        assert Cursor.pointer == "pointer"

    def test_overflow(self):
        assert Overflow.hidden == "hidden"
        assert Overflow.scroll == "scroll"
        assert Overflow.auto == "auto"

    def test_font_weight(self):
        assert FontWeight.bold == "bold"
        assert FontWeight.normal == "normal"

    def test_font_style(self):
        assert FontStyle.italic == "italic"
        assert FontStyle.normal == "normal"

    def test_box_sizing(self):
        assert BoxSizing.border_box == "border-box"
        assert BoxSizing.content_box == "content-box"

    def test_border_style(self):
        assert BorderStyle.solid == "solid"
        assert BorderStyle.dashed == "dashed"
        assert BorderStyle.none == "none"

    def test_visibility(self):
        assert Visibility.hidden == "hidden"
        assert Visibility.visible == "visible"

    def test_constants_are_strings(self):
        assert isinstance(Display.flex, str)
        assert isinstance(Position.absolute, str)
        assert isinstance(TextAlign.center, str)
