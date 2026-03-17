# HTML Elements

## Basics

Every standard HTML tag has a corresponding Python constructor. Pass children as positional arguments and set attributes with chained method calls.

```python
from ztml import *

Div(
    H1("Welcome"),
    P("Some text here."),
    A("Click me").href("/page").target("_blank"),
).cls("container").id("main")
```

This renders to:

```html
<div class="container" id="main">
  <h1>Welcome</h1>
  <p>Some text here.</p>
  <a href="/page" target="_blank">Click me</a>
</div>
```

Attribute methods mirror their HTML names. A few are adjusted to avoid Python keyword conflicts: `cls` instead of `class`, `for_` instead of `for`.

## Nesting

Elements nest naturally. Just pass them as children.

```python
Form(
    Div(
        Label("Email").for_("email"),
        Input().type("text").name("email").id("email"),
    ).cls("field"),
    Div(
        Label("Password").for_("pw"),
        Input().type("password").name("pw").id("pw"),
    ).cls("field"),
    Button("Log in").type("submit"),
).action("/login").method("post")
```

## Fragment

`Fragment` groups elements without adding a wrapper tag. Useful when a function needs to return multiple sibling elements.

```python
def user_info(name, email):
    return Fragment(
        H2(name),
        P(email),
    )
```

## Raw HTML

`Raw` injects unescaped HTML directly. Use it for trusted content you've built yourself. See the [security page](../reference/security.md) for important caveats.

```python
Fragment(
    H1("Title"),
    Raw("<hr/>"),
    P("After the rule."),
)
```

## Custom attributes

ztml generates all of its element constructors and attribute methods programmatically from JSON spec sheets. Just in case my parser missed something, or if you need something custom, you can use `.attr()`:

```python
Div("content").attr("data-page", "home").attr("x-data", "{open: false}")
```

## Rendering

Call `render()` to get an HTML string from any element, fragment, or component.

```python
html_string = render(Div("hello"))
# '<div>hello</div>'
```

When using the built-in server, rendering happens automatically for route return values. You just return the element and it handles the rest.
