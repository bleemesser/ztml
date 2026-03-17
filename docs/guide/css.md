# CSS Styling

## Rule

`Rule` is the main building block. It takes a CSS selector and exposes typed methods for every standard CSS property.

Note that things like `Rule` cannot be rendered on their own. They must be wrapped in a `Style` block.

```python
from ztml import *

Style(
    Rule("body").margin("0").font_family("system-ui, sans-serif"),
    Rule(".container").display("flex").gap("1rem").padding("2rem"),
    Rule(".sidebar").width("250px").flex_shrink("0"),
    Rule(".main").flex("1"),
)
```

The property methods are generated from W3C specs, so every standard property is available and your editor can autocomplete them. I wanted to improve on the experience in FastHTML where CSS is passed completely raw. Here, at least the property names are checked for you, and you don't have to write braces or `key: value;` items.

Values are still strings, since CSS values like `"1fr 2fr"` or `calc(100% - 20px)` cannot be easily represented in the type system. For properties with a known set of valid keywords, ztml exports enum-like constants you can use for discovery. See [CSS Enums](../reference/enums.md).

## Custom properties

For anything the generator missed, or vendor-prefixed properties, use `.prop()`:

```python
Rule(".grid").prop("-webkit-backdrop-filter", "blur(10px)")
```

## Media queries

`Media` wraps rules in a `@media` block.

```python
Media("max-width: 768px",
    Rule(".container").flex_direction("column"),
    Rule(".sidebar").width("100%"),
)
```

## Keyframes

`Keyframes` defines a `@keyframes` animation. Each step is a `Frame`.

```python
Keyframes("fadeIn",
    Frame("from").opacity("0").transform("translateY(-10px)"),
    Frame("to").opacity("1").transform("translateY(0)"),
)
```

Then reference it from a rule:

```python
Rule(".card").animation("fadeIn 0.3s ease-out")
```

## Style blocks

Wrap your rules, media queries, and keyframes in `Style()` to produce a `<style>` tag.

```python
Html(
    Head(
        Title("My Page"),
        Style(
            Rule("body").margin("0"),
            Rule(".content").max_width("800px").margin("0 auto"),
            Media("max-width: 600px",
                Rule(".content").padding("1rem"),
            ),
        ),
    ),
    Body(Div("hello").cls("content")),
)
```

## Inline styles

To affect only one element, `InlineStyle` lets you set styles directly.

```python
Div("alert").style(
    InlineStyle()
        .color("white")
        .background_color("#ef4444")
        .padding("0.75rem 1rem")
        .border_radius("6px")
)
```

## Composing styles

There's no dedicated theme system. I've found that plain Python does the job well enough. You can share styles through variables, functions, or whatever patterns you'd normally reach for. 

```python
page_style = Style(
    Rule("*").box_sizing("border-box").margin("0").padding("0"),
    Rule("body")
        .font_family("system-ui, sans-serif")
        .background_color("#f5f5f5"),
)

def layout(title, *children):
    return Html(
        Head(Title(title), page_style),
        Body(Div(*children).cls("content")),
    )
```

This keeps things simple. If you find yourself wanting a more structured approach, dataclasses or dicts work fine as theme objects. Just unpack them into your rules.
