"""A simple HTMX-powered todo app."""

from ztml import *
from ztml.server import rt, serve

todos: list[dict] = []
next_id = 0


def todo_item(todo: dict):
    done_cls = "done" if todo["done"] else ""
    return Li(
        Span(todo["text"]).cls("todo-text", done_cls),
        Button("✓").hx_post(f"/toggle/{todo['id']}").hx_target("#todo-list").hx_swap("innerHTML").cls("toggle"),
        Button("x").hx_delete(f"/delete/{todo['id']}").hx_target("#todo-list").hx_swap("innerHTML").cls("delete"),
    ).cls("todo-item")


def todo_list():
    return Fragment(*[todo_item(t) for t in todos])


@rt("/")
def get():
    return Html(
        Head(
            Title("Todos"),
            Style(
                Rule("*").box_sizing("border-box").margin("0").padding("0"),
                Rule("body")
                    .font_family("system-ui, sans-serif")
                    .background_color("#f5f5f5")
                    .display("flex")
                    .justify_content("center")
                    .padding("2rem"),
                Rule(".app")
                    .background_color("white")
                    .border_radius("12px")
                    .padding("2rem")
                    .width("100%")
                    .max_width("500px")
                    .prop("box-shadow", "0 4px 12px rgba(0,0,0,0.1)"),
                Rule("h1").margin_bottom("1rem"),
                Rule(".add-form")
                    .display("flex")
                    .gap("0.5rem")
                    .margin_bottom("1rem"),
                Rule(".add-form input")
                    .flex("1")
                    .padding("0.5rem 0.75rem")
                    .border("1px solid #ddd")
                    .border_radius("6px")
                    .font_size("1rem"),
                Rule(".add-form button")
                    .padding("0.5rem 1rem")
                    .background_color("#3b82f6")
                    .color("white")
                    .border("none")
                    .border_radius("6px")
                    .cursor("pointer"),
                Rule("#todo-list")
                    .list_style_type("none"),
                Rule(".todo-item")
                    .display("flex")
                    .align_items("center")
                    .gap("0.5rem")
                    .padding("0.5rem 0")
                    .border_bottom("1px solid #eee"),
                Rule(".todo-text")
                    .flex("1"),
                Rule(".done")
                    .text_decoration_line("line-through")
                    .color("#999"),
                Rule(".toggle, .delete")
                    .padding("0.25rem 0.5rem")
                    .border("none")
                    .border_radius("4px")
                    .cursor("pointer"),
                Rule(".toggle").background_color("#dcfce7").color("#166534"),
                Rule(".delete").background_color("#fee2e2").color("#991b1b"),
            ),
        ),
        Body(
            Div(
                H1("Todos"),
                Form(
                    Input().type("text").name("text").placeholder("What needs doing?").autofocus(),
                    Button("Add"),
                ).hx_post("/add").hx_target("#todo-list").hx_swap("innerHTML")
                 .cls("add-form").attr("hx-on::after-request", "this.reset()"),
                Ul(todo_list()).id("todo-list"),
            ).cls("app"),
        ),
    )


@rt("/add", methods=["POST"])
async def add_todo(request):
    global next_id
    form = await request.form()
    text = form.get("text", "").strip()
    if text:
        todos.append({"id": next_id, "text": text, "done": False})
        next_id += 1
    return todo_list()


@rt("/toggle/{todo_id}", methods=["POST"])
def toggle_todo(todo_id):
    for t in todos:
        if t["id"] == int(todo_id):
            t["done"] = not t["done"]
            break
    return todo_list()


@rt("/delete/{todo_id}", methods=["DELETE"])
def delete_todo(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != int(todo_id)]
    return todo_list()


serve()
