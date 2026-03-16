"""HTMX-powered counter app using the built-in server."""

from ztml import *
from ztml.server import rt, serve

count = 0


@rt("/")
def get():
    return Html(
        Head(
            Title("Counter"),
            Style(
                Rule("body")
                    .font_family("system-ui, sans-serif")
                    .display("flex")
                    .justify_content("center")
                    .align_items("center")
                    .min_height("100vh")
                    .margin("0")
                    .background_color("#f0f0f0"),
                Rule(".counter")
                    .text_align("center")
                    .background_color("white")
                    .padding("3rem")
                    .border_radius("12px")
                    .prop("box-shadow", "0 4px 12px rgba(0,0,0,0.1)"),
                Rule("#count")
                    .font_size("4rem")
                    .font_weight("bold")
                    .margin("1rem 0"),
                Rule(".buttons")
                    .display("flex")
                    .gap("1rem")
                    .justify_content("center"),
                Rule("button")
                    .padding("0.75rem 1.5rem")
                    .font_size("1.25rem")
                    .border("none")
                    .border_radius("8px")
                    .cursor("pointer")
                    .color("white"),
                Rule(".dec").background_color("#ef4444"),
                Rule(".inc").background_color("#22c55e"),
                Rule(".reset").background_color("#6b7280"),
            ),
        ),
        Body(
            Div(
                H1("Counter"),
                P(str(count)).id("count"),
                Div(
                    Button("-").hx_post("/decrement").hx_target("#count").cls("dec"),
                    Button("Reset").hx_post("/reset").hx_target("#count").cls("reset"),
                    Button("+").hx_post("/increment").hx_target("#count").cls("inc"),
                ).cls("buttons"),
            ).cls("counter"),
        ),
    )


@rt("/increment", methods=["POST"])
def increment():
    global count
    count += 1
    return P(str(count)).id("count")


@rt("/decrement", methods=["POST"])
def decrement():
    global count
    count -= 1
    return P(str(count)).id("count")


@rt("/reset", methods=["POST"])
def reset():
    global count
    count = 0
    return P(str(count)).id("count")


if __name__ == "__main__":
    serve()
