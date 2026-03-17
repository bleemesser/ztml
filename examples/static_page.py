"""Generate a static HTML page with styled components and interactivity."""

from ztml import *

page = Html(
    Head(
        Meta().charset("utf-8"),
        Meta().name("viewport").content("width=device-width, initial-scale=1"),
        Title("ztml — Static Page Example"),
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
            Rule("h1")
                .font_size("2.5rem")
                .margin_bottom("0.5rem"),
            Rule(".subtitle")
                .color("#666")
                .margin_bottom("2rem"),
            Rule(".card")
                .background_color("white")
                .border_radius("8px")
                .padding("1.5rem")
                .margin_bottom("1rem")
                .box_shadow("0 2px 4px rgba(0,0,0,0.1)"),
            Rule(".card h2")
                .font_size("1.25rem")
                .margin_bottom("0.5rem"),
            Rule(".tag")
                .display("inline-block")
                .padding("0.25rem 0.75rem")
                .border_radius("999px")
                .font_size("0.875rem")
                .margin_right("0.5rem")
                .margin_bottom("0.5rem"),
            Rule(".tag--blue")
                .background_color("#dbeafe")
                .color("#1e40af"),
            Rule(".tag--green")
                .background_color("#dcfce7")
                .color("#166534"),
            Rule("button")
                .padding("0.5rem 1rem")
                .border_radius("6px")
                .border("none")
                .background_color("#3b82f6")
                .color("white")
                .font_size("1rem")
                .cursor("pointer"),
            Rule("button:hover")
                .background_color("#2563eb"),
            Keyframes("fadeIn",
                Frame("from").opacity("0").transform("translateY(10px)"),
                Frame("to").opacity("1").transform("translateY(0)"),
            ),
            Rule(".card")
                .animation("fadeIn 0.4s ease-out"),
        ),
    ),
    Body(
        Div(
            H1("ztml"),
            P("A Rust-backed framework for building websites in pure Python.").cls("subtitle"),
            Div(
                H2("HTML"),
                P("Every HTML element has a constructor. Attributes are set via chained methods."),
                Div(
                    Span("Typed").cls("tag", "tag--blue"),
                    Span("Composable").cls("tag", "tag--green"),
                    Span("Autocomplete").cls("tag", "tag--blue"),
                ),
            ).cls("card"),
            Div(
                H2("CSS"),
                P("Build stylesheets with Rule, Media, and Keyframes — all in Python."),
            ).cls("card"),
            Div(
                H2("JavaScript"),
                P("Attach event handlers with On.click, On.submit, and more."),
                Button("Click me").id("demo-btn"),
            ).cls("card"),
            Script(
                On.click("#demo-btn", "alert('Hello from ztml!')"),
            ),
        ).cls("container"),
    ),
)

print(render(page))
