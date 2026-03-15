use indexmap::IndexMap;

use crate::css::{CssItem, CssRule};
use crate::element::{AttrValue, Child, Element};
use crate::script::{EventHandler, ScriptItem};

/// Serialize an element tree into an HTML string
pub fn render_element(el: &Element) -> String {
    let mut out = String::new();
    render_element_into(el, &mut out);
    out
}

/// Serialize a list of CSS items into a CSS string
pub fn render_stylesheet(items: &[CssItem]) -> String {
    let mut out = String::new();
    for item in items {
        render_css_item(item, &mut out);
    }
    out
}

/// Render CSS properties as a semicolon-separated inline style string
pub fn render_inline_style(properties: &IndexMap<String, String>) -> String {
    let mut out = String::new();
    for (i, (prop, val)) in properties.iter().enumerate() {
        if i > 0 {
            out.push_str("; ");
        }

        out.push_str(prop);
        out.push_str(": ");
        out.push_str(val);
    }

    out
}

/// Serialize a list of script items into JS code
pub fn render_script(items: &[ScriptItem]) -> String {
    let mut out = String::new();
    for item in items {
        match item {
            ScriptItem::Handler(h) => render_event_handler(h, &mut out),
            ScriptItem::Raw(s) => out.push_str(s),
        }
    }

    out
}

/// Recursively convert an element and its children into valid HTML,
/// mutating the provided String
fn render_element_into(el: &Element, out: &mut String) {
    out.push('<');
    out.push_str(&el.tag);

    for (name, value) in &el.attrs {
        match value {
            AttrValue::String(s) => {
                out.push(' ');
                out.push_str(name);
                out.push_str("=\"");
                out.push_str(&escape_attr(s));
                out.push('"');
            }
            AttrValue::Bool(true) => {
                out.push(' ');
                out.push_str(name);
            }
            AttrValue::Bool(false) => {}
        }
    }

    out.push('>');

    if el.self_closing {
        return;
    }

    for child in &el.children {
        render_child_into(child, out);
    }

    out.push_str("</");
    out.push_str(&el.tag);
    out.push('>');
}

/// Render a single child node into the provided String
pub fn render_child_into(child: &Child, out: &mut String) {
    match child {
        Child::Text(s) => out.push_str(&escape_html(s)),
        Child::Raw(s) => out.push_str(s),
        Child::Node(el) => render_element_into(el, out),
        Child::Fragment(children) => {
            for c in children {
                render_child_into(c, out);
            }
        }
    }
}

/// Escape a string for use in an HTML attribute value
fn escape_attr(s: &str) -> String {
    escape_html(s)
}

/// Escape  `&`, `<`, `>`, and `"` from a string for use in HTML text
fn escape_html(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            _ => out.push(c),
        }
    }
    out
}

/// Render a CSS item into a string
fn render_css_item(item: &CssItem, out: &mut String) {
    match item {
        CssItem::Rule(rule) => render_css_rule(rule, out),
        CssItem::Media(mq) => {
            out.push_str("@media (");
            out.push_str(&mq.query);
            out.push_str(") {\n");
            for rule in &mq.rules {
                render_css_rule(rule, out);
            }
            out.push_str("}\n");
        }
        CssItem::Keyframes(kf) => {
            out.push_str("@keyframes ");
            out.push_str(&kf.name);
            out.push_str(" {\n");
            for step in &kf.steps {
                out.push_str(&step.selector);
                out.push_str(" {\n");
                for (prop, val) in &step.properties {
                    out.push_str("  ");
                    out.push_str(prop);
                    out.push_str(": ");
                    out.push_str(val);
                    out.push_str(";\n");
                }
                out.push_str("}\n");
            }
            out.push_str("}\n");
        }
        CssItem::Raw(s) => out.push_str(s),
    }
}

/// Render a CSS rule into a rule block string
fn render_css_rule(rule: &CssRule, out: &mut String) {
    out.push_str(&rule.selector);
    out.push_str(" {\n");
    for (prop, val) in &rule.properties {
        out.push_str("  ");
        out.push_str(prop);
        out.push_str(": ");
        out.push_str(val);
        out.push_str(";\n");
    }
    out.push_str("}\n");
}

/// Render an event handler as a `document.addEventListener` call.
/// Selectors will be applied using `e.target.matches()` except for on
/// `DOMContentLoaded` handlers, where the match is omitted.
fn render_event_handler(handler: &EventHandler, out: &mut String) {
    if handler.event == "DOMContentLoaded" {
        out.push_str("document.addEventListener('DOMContentLoaded', function() { ");
        out.push_str(&handler.js);
        out.push_str(" });\n");
    } else {
        out.push_str("document.addEventListener('");
        out.push_str(&handler.event);
        out.push_str("', function(e) {\n");
        out.push_str("    if (e.target.matches('");
        out.push_str(&handler.selector);
        out.push_str("')) { ");
        out.push_str(&handler.js);
        out.push_str(" }\n");
        out.push_str("});\n");
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_element() {
        let mut el = Element::new("div", false);
        el.add_child(Child::Text("hello".into()));
        assert_eq!(render_element(&el), "<div>hello</div>");
    }

    #[test]
    fn test_void_element() {
        let el = Element::new("br", true);
        assert_eq!(render_element(&el), "<br>");
    }

    #[test]
    fn test_attrs() {
        let mut el = Element::new("div", false);
        el.set_attr("id", AttrValue::String("main".into()));
        el.set_attr("hidden", AttrValue::Bool(true));
        assert_eq!(render_element(&el), "<div id=\"main\" hidden></div>");
    }

    #[test]
    fn test_class_append() {
        let mut el = Element::new("div", false);
        el.append_class("a");
        el.append_class("b");
        assert_eq!(render_element(&el), "<div class=\"a b\"></div>");
    }

    #[test]
    fn test_escape() {
        let mut el = Element::new("p", false);
        el.add_child(Child::Text("<script>alert('xss')</script>".into()));
        assert_eq!(
            render_element(&el),
            "<p>&lt;script&gt;alert('xss')&lt;/script&gt;</p>"
        );
    }

    #[test]
    fn test_nested() {
        let mut h1 = Element::new("h1", false);
        h1.add_child(Child::Text("hello".into()));
        let mut div = Element::new("div", false);
        div.append_class("main");
        div.add_child(Child::Node(h1));
        assert_eq!(
            render_element(&div),
            "<div class=\"main\"><h1>hello</h1></div>"
        );
    }
}
