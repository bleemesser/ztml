"""Demo app showcasing sessions, before hooks, and form data parsing."""

from dataclasses import dataclass
from starlette.responses import RedirectResponse

from ztml import *
from ztml.server import ZTMLApp, serve

app = ZTMLApp(session_secret="change-me-in-production", dev=True)

@dataclass
class Alert:
    message: str
    color: str = "#3b82f6"

    def __ztml_render__(self):
        return Div(self.message).style(
            InlineStyle()
            .padding("0.75rem 1rem")
            .border_radius("6px")
            .color("white")
            .background_color(self.color)
            .margin_bottom("1rem")
        )


def require_auth(session):
    if not session.get("user"):
        return RedirectResponse("/login", status_code=303)


page_style = Style(
    Rule("*").box_sizing("border-box").margin("0").padding("0"),
    Rule("body")
        .font_family("system-ui, sans-serif")
        .background_color("#f5f5f5")
        .display("flex")
        .justify_content("center")
        .padding("2rem"),
    Rule(".card")
        .background_color("white")
        .border_radius("12px")
        .padding("2rem")
        .width("100%")
        .max_width("400px")
        .box_shadow("0 4px 12px rgba(0,0,0,0.1)"),
    Rule("h1").margin_bottom("1rem"),
    Rule("input, button")
        .padding("0.5rem 0.75rem")
        .border("1px solid #ddd")
        .border_radius("6px")
        .font_size("1rem")
        .width("100%"),
    Rule("input").margin_bottom("0.75rem"),
    Rule("button")
        .background_color("#3b82f6")
        .color("white")
        .border("none")
        .cursor("pointer")
        .margin_top("0.5rem"),
    Rule("a").color("#3b82f6"),
)


def layout(*children):
    return Html(
        Head(Title("Auth Demo"), page_style),
        Body(Div(*children).cls("card")),
    )


@app.route("/login")
def login_page(session):
    children: list = [H1("Login")]
    if session.get("error"):
        children.append(Alert(session.pop("error"), color="#ef4444"))
    children.append(
        Form(
            Input().type("text").name("username").placeholder("Username").autofocus(),
            Input().type("password").name("password").placeholder("Password"),
            Button("Log in"),
        ).method("post").action("/login")
    )
    return layout(*children)


@app.route("/login", methods=["POST"])
def login(session, form_data):
    username = form_data.get("username", "").strip()
    password = form_data.get("password", "")
    if username and password == "secret":
        session["user"] = username
        return RedirectResponse("/dashboard", status_code=303)
    session["error"] = "Invalid credentials (hint: password is 'secret')"
    return RedirectResponse("/login", status_code=303)


@app.route("/dashboard", before=[require_auth])
def dashboard(session):
    user = session["user"]
    return layout(
        H1(f"Welcome, {user}!"),
        Alert(f"You are logged in as {user}."),
        P(A("Log out").href("/logout")),
    )


@app.route("/logout")
def logout(session):
    session.clear()
    return RedirectResponse("/login", status_code=303)


@app.route("/")
def index():
    return RedirectResponse("/dashboard", status_code=303)


if __name__ == "__main__":
    serve(target=app)
