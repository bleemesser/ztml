# Custom Components

## The `__ztml_render__` protocol

Any Python object with a `__ztml_render__` method can be used wherever ztml expects an element. The method should return a ztml element (or fragment, or another renderable).

```python
from ztml import *

class Card:
    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __ztml_render__(self):
        return Div(
            H2(self.title),
            P(self.body),
        ).cls("card")
```

Once a class has this method, you can pass it directly to `render()`, nest them inside elements, or return them from server routes.

```python
page = Div(
    Card("First", "Some content"),
    Card("Second", "More content"),
).cls("cards")
```

I went with a protocol instead of inheritance because it plays nicely with dataclasses, existing class hierarchies, and general Python conventions.

## Dataclasses

Dataclasses work especially well as components since they give you `__init__` for free.

```python
from dataclasses import dataclass

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
        )
```

## Jupyter and Jinja2

All built-in ztml elements implement `_repr_html_()` for Jupyter display and `__html__()` for Jinja2/MarkupSafe auto-escaping. Evaluating an element at the end of a Jupyter cell renders it as HTML automatically.

For custom components, add these methods yourself:

```python
class Card:
    def __init__(self, title, body):
        self.title = title
        self.body = body

    def __ztml_render__(self):
        return Div(H2(self.title), P(self.body)).cls("card")

    def __html__(self): # -> str
        return render(self) # `from ztml import render` if you need it

    def _repr_html_(self): # -> str
        return render(self)
```


