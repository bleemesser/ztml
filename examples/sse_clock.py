"""Server-Sent Events clock using ztml."""

from datetime import datetime

from ztml import *
from ztml.scripts import HTMX, HTMX_SSE
from ztml.server import ZTMLApp, NamedEventStream, serve

app = ZTMLApp(dev=True)

clock = NamedEventStream(interval=1)


@clock.source("time")
def time_event():
    return datetime.now().strftime("%H:%M:%S")


@clock.source("date")
def date_event():
    return datetime.now().strftime("%A, %B %d, %Y")


@app.route("/clock")
async def clock_route():
    return clock.response()


@app.route("/")
def get():
    return Html(
        Head(
            Title("SSE Clock"),
            Style(
                Rule("*").box_sizing("border-box").margin("0").padding("0"),
                Rule("body")
                    .font_family("system-ui, sans-serif")
                    .background_color("#f5f5f5")
                    .display("flex")
                    .justify_content("center")
                    .align_items("center")
                    .min_height("100vh"),
                Rule(".clock")
                    .background_color("white")
                    .border_radius("12px")
                    .padding("3rem")
                    .text_align("center")
                    .box_shadow("0 4px 12px rgba(0,0,0,0.1)"),
                Rule("h1").margin_bottom("1rem").color("#374151"),
                Rule("#time")
                    .font_size("4rem")
                    .font_weight("bold")
                    .color("#3b82f6")
                    .font_variant_numeric("tabluar-nums"),
                Rule("#date")
                    .font_size("1.25rem")
                    .color("#6b7280")
                    .margin_top("0.5rem"),
            ),
            HTMX, HTMX_SSE,
        ),
        Body(
            Div(
                H1("SSE Clock"),
                Div(
                    Div("--:--:--").id("time").attr("sse-swap", "time"),
                    Div("---").id("date").attr("sse-swap", "date"),
                ).hx_ext("sse").attr("sse-connect", "/clock"),
            ).cls("clock"),
        ),
    )


if __name__ == "__main__":
    serve(target=app)
