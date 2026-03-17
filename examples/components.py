"""Reusable components using the __ztml_render__ protocol."""

from ztml import *


class Card:
    def __init__(self, title, *children, id=None):
        self.title = title
        self.children = children
        self.id = id

    def __ztml_render__(self):
        card = Div(H2(self.title), *self.children).cls("card")
        if self.id:
            card = card.id(self.id)
        return card


class Badge:
    def __init__(self, label, color="blue"):
        self.label = label
        self.color = color

    def __ztml_render__(self):
        return Span(self.label).cls("badge", f"badge--{self.color}")


class NavLink:
    def __init__(self, text, href):
        self.text = text
        self.href = href

    def __ztml_render__(self):
        return Li(A(self.text).href(self.href)).cls("nav-link")


class Navbar:
    def __init__(self, *links):
        self.links = links

    def __ztml_render__(self):
        return Nav(Ul(*self.links)).cls("nav")


class Page:
    def __init__(self, title, *children):
        self.title = title
        self.children = children

    def __ztml_render__(self):
        return Html(
            Head(
                Meta().charset("utf-8"),
                Meta().name("viewport").content("width=device-width, initial-scale=1"),
                Title(self.title),
                Style(
                    Rule("*").box_sizing("border-box").margin("0").padding("0"),
                    Rule("body")
                        .font_family("system-ui, -apple-system, sans-serif")
                        .line_height("1.6")
                        .color("#1a1a2e")
                        .background_color("#f5f5f5"),
                    Rule(".container")
                        .max_width("800px")
                        .margin("0 auto")
                        .padding("2rem"),
                    Rule(".nav ul")
                        .list_style("none")
                        .display("flex")
                        .gap("1rem")
                        .padding("1rem 0")
                        .border_bottom("1px solid #ddd")
                        .margin_bottom("2rem"),
                    Rule(".nav a")
                        .text_decoration("none")
                        .color("#3b82f6"),
                    Rule(".nav a:hover")
                        .text_decoration("underline"),
                    Rule("h1")
                        .font_size("2rem")
                        .margin_bottom("1.5rem"),
                    Rule(".card")
                        .background_color("white")
                        .border_radius("8px")
                        .padding("1.5rem")
                        .margin_bottom("1rem")
                        .box_shadow("0 2px 4px rgba(0,0,0,0.1)"),
                    Rule(".card h2")
                        .font_size("1.25rem")
                        .margin_bottom("0.5rem"),
                    Rule(".badge")
                        .display("inline-block")
                        .padding("0.2rem 0.6rem")
                        .border_radius("999px")
                        .font_size("0.8rem")
                        .margin_right("0.5rem"),
                    Rule(".badge--blue")
                        .background_color("#dbeafe")
                        .color("#1e40af"),
                    Rule(".badge--green")
                        .background_color("#dcfce7")
                        .color("#166534"),
                    Rule(".badge--red")
                        .background_color("#fee2e2")
                        .color("#991b1b"),
                ),
            ),
            Body(
                Div(
                    *self.children,
                ).cls("container"),
            ),
        )


# Build the page using components

page = Page(
    "Component Demo",
    Navbar(
        NavLink("Protocol", "#protocol"),
        NavLink("Composable", "#composable"),
        NavLink("Reusable", "#reusable"),
    ),
    H1("Custom Components"),
    Card(
        "What is __ztml_render__?",
        P("Any Python class with a __ztml_render__ method can be used as a ztml component."),
        P("The method returns a ztml element, which gets rendered like any other."),
        id="protocol",
    ),
    Card(
        "Composable",
        P("Components nest inside elements and other components freely:"),
        Div(
            Badge("Python", "blue"),
            Badge("Rust", "red"),
            Badge("Fast", "green"),
        ),
        id="composable",
    ),
    Card(
        "Reusable",
        P("Define once, use everywhere — just like a function, but with state."),
        id="reusable",
    ),
)

print(render(page))
