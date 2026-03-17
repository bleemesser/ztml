# CSS Enums

## What they are

ztml exports enum-like classes for CSS properties that have a fixed set of valid keyword values. These are generated from the same W3C specs as the property methods.

```python
from ztml import Display, Position, FlexDirection, TextAlign

Display.flex        # "flex"
Display.grid        # "grid"
Position.sticky     # "sticky"
FlexDirection.column  # "column"
```

The values are plain strings, so they work anywhere a string does.

## Why they exist

The main value is discoverability. If you type `Display.` in your editor, autocomplete shows you every valid keyword for the `display` property. That's useful when you can't remember whether it's `inline-flex` or `inlineFlex` (it's `inline_flex` on the enum, which maps to `"inline-flex"`).

You don't have to use them. String literals work identically:

```python
# These are equivalent
Rule(".box").display(Display.flex)
Rule(".box").display("flex")
```

I'd recommend using string literals in most cases since they're shorter and read more like actual CSS. The enums are there when you want to explore what's available or when you're working with a property you're less familiar with.

## Coverage

There are around 300 enum classes covering most CSS properties with keyword values. Some examples:

- Layout: `Display`, `Position`, `FlexDirection`, `FlexWrap`, `GridAutoFlow`
- Alignment: `AlignContent`, `AlignItems`, `AlignSelf`, `JustifyContent`
- Typography: `FontWeight`, `TextAlign`, `TextDecoration`, `WhiteSpace`
- Box model: `BoxSizing`, `Overflow`, `BorderStyle`, `BorderCollapse`
- Visual: `Visibility`, `Opacity`, `Cursor`, `PointerEvents`

There are also a handful of HTML attribute enums like `InputType`, `ButtonType`, and `FormMethod`.

Properties that take freeform values (colors, lengths, `calc()` expressions, custom properties) don't have enums for obvious reasons.
