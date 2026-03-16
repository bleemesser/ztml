"""Server-Sent Events clock using ztml."""

import asyncio
from datetime import datetime

from ztml import *
from ztml.server import ZTMLApp, serve
from starlette.responses import StreamingResponse

app = ZTMLApp(dev=True)

SSE_EXT = '<script src="https://unpkg.com/htmx-ext-sse@2.2.2/sse.js"></script>'

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
                    .prop("box-shadow", "0 4px 12px rgba(0,0,0,0.1)"),
                Rule("h1").margin_bottom("1rem").color("#374151"),
                Rule("#time")
                    .font_size("4rem")
                    .font_weight("bold")
                    .color("#3b82f6")
                    .prop("font-variant-numeric", "tabular-nums"),
                Rule("#date")
                    .font_size("1.25rem")
                    .color("#6b7280")
                    .margin_top("0.5rem"),
            ),
            Raw(SSE_EXT),
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


async def clock_stream():
    while True:
        now = datetime.now()
        yield f"event: time\ndata: {now.strftime('%H:%M:%S')}\n\n"
        yield f"event: date\ndata: {now.strftime('%A, %B %d, %Y')}\n\n"
        await asyncio.sleep(1)


@app.route("/clock")
async def clock():
    return StreamingResponse(clock_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    serve(target=app)
