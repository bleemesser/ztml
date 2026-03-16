"""WebSocket chat room using ztml."""

from ztml import *
from ztml.server import ZTMLApp, serve

app = ZTMLApp(dev=True)

@app.route("/")
def get():
    return Html(
        Head(
            Title("WebSocket Chat"),
            Style(
                Rule("*").box_sizing("border-box").margin("0").padding("0"),
                Rule("body")
                    .font_family("system-ui, sans-serif")
                    .background_color("#f5f5f5")
                    .display("flex")
                    .justify_content("center")
                    .padding("2rem"),
                Rule(".chat")
                    .background_color("white")
                    .border_radius("12px")
                    .padding("2rem")
                    .width("100%")
                    .max_width("500px")
                    .prop("box-shadow", "0 4px 12px rgba(0,0,0,0.1)"),
                Rule("h1").margin_bottom("1rem"),
                Rule("#messages")
                    .height("300px")
                    .overflow_y("auto")
                    .border("1px solid #ddd")
                    .border_radius("6px")
                    .padding("0.75rem")
                    .margin_bottom("1rem"),
                Rule(".msg")
                    .padding("0.25rem 0")
                    .border_bottom("1px solid #f0f0f0"),
                Rule(".msg b").color("#3b82f6"),
                Rule(".send-form")
                    .display("flex")
                    .gap("0.5rem"),
                Rule(".send-form input")
                    .flex("1")
                    .padding("0.5rem 0.75rem")
                    .border("1px solid #ddd")
                    .border_radius("6px")
                    .font_size("1rem"),
                Rule(".send-form button")
                    .padding("0.5rem 1rem")
                    .background_color("#3b82f6")
                    .color("white")
                    .border("none")
                    .border_radius("6px")
                    .cursor("pointer")
                    .font_size("1rem"),
            ),
        ),
        Body(
            Div(
                H1("Chat"),
                Div().id("messages"),
                Div(
                    Input().type("text").id("msg").placeholder("Type a message...").autofocus(),
                    Button("Send").id("send"),
                ).cls("send-form"),
            ).cls("chat"),
            Script(
                RawJs("""
                    const ws = new WebSocket("ws://" + location.host + "/ws");
                    const messages = document.getElementById("messages");

                    ws.onmessage = function(e) {
                        const div = document.createElement("div");
                        div.className = "msg";
                        div.innerHTML = e.data;
                        messages.appendChild(div);
                        messages.scrollTop = messages.scrollHeight;
                    };

                    function sendMsg() {
                        const input = document.getElementById("msg");
                        const text = input.value.trim();
                        if (text) {
                            ws.send(text);
                            input.value = "";
                        }
                    }
                """),
                On.click("#send", "sendMsg()"),
                On.keydown("#msg", """
                    if (event.key === "Enter") sendMsg();
                """),
            ),
        ),
    )


clients: set = set()

@app.ws("/ws")
async def chat(websocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            html = render(Span(B("user: "), text))
            for client in list(clients):
                try:
                    await client.send_text(html)
                except Exception:
                    clients.discard(client)
    except Exception:
        clients.discard(websocket)


if __name__ == "__main__":
    serve(target=app)
