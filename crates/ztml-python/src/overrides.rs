//! Hand-written types and attributes not derivable from any spec:
//! - PyElement: wraps core Element, exposes global HTML attrs, per-element attrs, and HTMX attrs
//! - Fragment: renders children without a wrapper element
//! - Raw: injects unescaped HTML
//! - Custom: creates elements with arbitrary tag names
//! - HxSwap: enum-like class for HTMX swap strategy values
//!
//! The repetitive method pattern (one fn per attribute) is inherent to PyO3 —
//! proc macros can't expand inside `#[pymethods]` blocks.

use pyo3::prelude::*;
use pyo3::types::{PyFloat, PyList, PyString};
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pyfunction, gen_stub_pymethods};
use ztml_core::element::{AttrValue, Child, Element};
use ztml_core::render::{render_script, render_stylesheet};

use crate::css::PyStyle;
use crate::script::PyScript;

/// Wrap a core `Element` for Python exposure with chainable attribute setters
#[gen_stub_pyclass]
#[pyclass(name = "Element", skip_from_py_object)]
#[derive(Clone)]
pub struct PyElement {
    pub inner: Element,
}

impl PyElement {
    /// Create a `PyElement` wrapping a core `Element` with the given children
    pub fn create(tag: &str, self_closing: bool, children: Vec<Child>) -> Self {
        let mut el = Element::new(tag, self_closing);
        el.children = children;
        Self { inner: el }
    }
}

/// Global HTML attributes + per-element attributes + HTMX attributes.
/// All defined on PyElement; .pyi stubs restrict per-element visibility.
#[gen_stub_pymethods]
#[pymethods]
impl PyElement {
    // Global HTML attributes:
    fn id(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("id", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (*classes))]
    fn cls(mut slf: PyRefMut<'_, Self>, classes: Vec<String>) -> PyRefMut<'_, Self> {
        for c in classes { slf.inner.append_class(&c); }
        slf
    }
    fn style<'a>(mut slf: PyRefMut<'a, Self>, value: Bound<'a, PyAny>) -> PyResult<PyRefMut<'a, Self>> {
        let css_string = if let Ok(s) = value.extract::<String>() {
            s
        } else if let Ok(inline) = value.cast::<crate::css::PyInlineStyle>() {
            let borrowed = inline.borrow();
            borrowed.properties.iter().map(|(k, v)| format!("{}: {}", k, v)).collect::<Vec<_>>().join("; ")
        } else {
            return Err(pyo3::exceptions::PyTypeError::new_err("style() expects a str or InlineStyle"));
        };
        slf.inner.set_attr("style", AttrValue::String(css_string));
        Ok(slf)
    }
    #[pyo3(name = "title")]
    fn set_title(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("title", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn hidden(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hidden", AttrValue::Bool(value)); slf
    }
    fn tabindex(mut slf: PyRefMut<'_, Self>, value: i32) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("tabindex", AttrValue::String(value.to_string())); slf
    }
    fn role(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("role", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn draggable(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("draggable", AttrValue::String(value.to_string())); slf
    }
    #[pyo3(signature = (value=true))]
    fn contenteditable(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("contenteditable", AttrValue::String(value.to_string())); slf
    }
    fn data(mut slf: PyRefMut<'_, Self>, name: String, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr(format!("data-{name}"), AttrValue::String(value)); slf
    }
    fn aria(mut slf: PyRefMut<'_, Self>, name: String, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr(format!("aria-{name}"), AttrValue::String(value)); slf
    }
    fn attr(mut slf: PyRefMut<'_, Self>, name: String, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr(name, AttrValue::String(value)); slf
    }

    // Per-element attributes (all on PyElement, stubs restrict per-element):
    fn href(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("href", AttrValue::String(value)); slf
    }
    fn target(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("target", AttrValue::String(value)); slf
    }
    fn rel(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("rel", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn download(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("download", AttrValue::Bool(value)); slf
    }
    fn src(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("src", AttrValue::String(value)); slf
    }
    fn alt(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("alt", AttrValue::String(value)); slf
    }
    fn width(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("width", AttrValue::String(value)); slf
    }
    fn height(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("height", AttrValue::String(value)); slf
    }
    fn loading(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("loading", AttrValue::String(value)); slf
    }
    #[pyo3(name = "type")]
    fn type_(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("type", AttrValue::String(value)); slf
    }
    fn name(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("name", AttrValue::String(value)); slf
    }
    fn value(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("value", AttrValue::String(value)); slf
    }
    fn placeholder(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("placeholder", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn required(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("required", AttrValue::Bool(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn disabled(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("disabled", AttrValue::Bool(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn autofocus(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("autofocus", AttrValue::Bool(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn checked(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("checked", AttrValue::Bool(value)); slf
    }
    fn min(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("min", AttrValue::String(value)); slf
    }
    fn max(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("max", AttrValue::String(value)); slf
    }
    fn pattern(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("pattern", AttrValue::String(value)); slf
    }
    fn action(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("action", AttrValue::String(value)); slf
    }
    fn method(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("method", AttrValue::String(value)); slf
    }
    fn enctype(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("enctype", AttrValue::String(value)); slf
    }
    fn html_for(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("for", AttrValue::String(value)); slf
    }
    fn rows(mut slf: PyRefMut<'_, Self>, value: i32) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("rows", AttrValue::String(value.to_string())); slf
    }
    fn cols(mut slf: PyRefMut<'_, Self>, value: i32) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("cols", AttrValue::String(value.to_string())); slf
    }
    #[pyo3(signature = (value=true))]
    fn multiple(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("multiple", AttrValue::Bool(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn selected(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("selected", AttrValue::Bool(value)); slf
    }
    fn colspan(mut slf: PyRefMut<'_, Self>, value: i32) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("colspan", AttrValue::String(value.to_string())); slf
    }
    fn rowspan(mut slf: PyRefMut<'_, Self>, value: i32) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("rowspan", AttrValue::String(value.to_string())); slf
    }
    fn scope(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("scope", AttrValue::String(value)); slf
    }
    fn content(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("content", AttrValue::String(value)); slf
    }
    fn charset(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("charset", AttrValue::String(value)); slf
    }
    fn http_equiv(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("http-equiv", AttrValue::String(value)); slf
    }
    fn media(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("media", AttrValue::String(value)); slf
    }

    // HTMX attributes (not in any W3C spec):
    fn hx_get(mut slf: PyRefMut<'_, Self>, url: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-get", AttrValue::String(url)); slf
    }
    fn hx_post(mut slf: PyRefMut<'_, Self>, url: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-post", AttrValue::String(url)); slf
    }
    fn hx_put(mut slf: PyRefMut<'_, Self>, url: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-put", AttrValue::String(url)); slf
    }
    fn hx_patch(mut slf: PyRefMut<'_, Self>, url: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-patch", AttrValue::String(url)); slf
    }
    fn hx_delete(mut slf: PyRefMut<'_, Self>, url: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-delete", AttrValue::String(url)); slf
    }
    fn hx_target(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-target", AttrValue::String(value)); slf
    }
    fn hx_swap(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-swap", AttrValue::String(value)); slf
    }
    fn hx_trigger(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-trigger", AttrValue::String(value)); slf
    }
    fn hx_confirm(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-confirm", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn hx_boost(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-boost", AttrValue::String(value.to_string())); slf
    }
    fn hx_push_url(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-push-url", AttrValue::String(value)); slf
    }
    fn hx_select(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-select", AttrValue::String(value)); slf
    }
    fn hx_select_oob(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-select-oob", AttrValue::String(value)); slf
    }
    fn hx_swap_oob(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-swap-oob", AttrValue::String(value)); slf
    }
    fn hx_vals(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-vals", AttrValue::String(value)); slf
    }
    fn hx_include(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-include", AttrValue::String(value)); slf
    }
    fn hx_indicator(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-indicator", AttrValue::String(value)); slf
    }
    #[pyo3(signature = (value=true))]
    fn hx_disable(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-disable", AttrValue::Bool(value)); slf
    }
    fn hx_encoding(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-encoding", AttrValue::String(value)); slf
    }
    fn hx_ext(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-ext", AttrValue::String(value)); slf
    }
    fn hx_headers(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr("hx-headers", AttrValue::String(value)); slf
    }
    fn hx_on(mut slf: PyRefMut<'_, Self>, event: String, js: String) -> PyRefMut<'_, Self> {
        slf.inner.set_attr(format!("hx-on::{event}"), AttrValue::String(js)); slf
    }
}

/// Create an element with an arbitrary tag name
#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (tag, *args))]
pub fn Custom(tag: &str, args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<PyElement> {
    let children = py_to_children(args)?;
    Ok(PyElement::create(tag, false, children))
}

/// Render children without a wrapper element
#[gen_stub_pyclass]
#[pyclass(skip_from_py_object)]
#[derive(Clone)]
pub struct Fragment {
    pub children: Vec<Child>,
}

#[gen_stub_pymethods]
#[pymethods]
impl Fragment {
    #[new]
    #[pyo3(signature = (*args))]
    fn new(args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<Self> {
        let children = py_to_children(args)?;
        Ok(Self { children })
    }
}

/// Inject unescaped HTML verbatim
#[gen_stub_pyclass]
#[pyclass(skip_from_py_object)]
#[derive(Clone)]
pub struct Raw(pub String);

#[gen_stub_pymethods]
#[pymethods]
impl Raw {
    #[new]
    fn new(text: &str) -> Self { Self(text.to_string()) }
}

/// HTMX swap strategy constants
#[gen_stub_pyclass]
#[pyclass(name = "HxSwap", skip_from_py_object)]
#[derive(Clone)]
pub struct HxSwap;

#[gen_stub_pymethods]
#[pymethods]
impl HxSwap {
    #[classattr] fn innerHTML() -> String { "innerHTML".into() }
    #[classattr] fn outerHTML() -> String { "outerHTML".into() }
    #[classattr] fn beforebegin() -> String { "beforebegin".into() }
    #[classattr] fn afterbegin() -> String { "afterbegin".into() }
    #[classattr] fn beforeend() -> String { "beforeend".into() }
    #[classattr] fn afterend() -> String { "afterend".into() }
    #[classattr] fn delete() -> String { "delete".into() }
    #[classattr] fn none() -> String { "none".into() }
}

/// Register hand-written overrides on the Python module
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyElement>()?;
    m.add_class::<Fragment>()?;
    m.add_class::<Raw>()?;
    m.add_class::<HxSwap>()?;
    m.add_function(pyo3::wrap_pyfunction!(Custom, m)?)?;
    Ok(())
}

/// Convert a Python `*args` tuple into a `Vec<Child>`, recursively resolving
/// strings, elements, fragments, lists, numbers, `None`, and the `__ztml_render__` protocol
pub fn py_to_children(args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<Vec<Child>> {
    let mut children = Vec::new();
    for arg in args.iter() {
        collect_child(&arg, &mut children)?;
    }
    Ok(children)
}

/// Resolve a single Python object into one or more `Child` values
fn collect_child(obj: &Bound<'_, pyo3::PyAny>, out: &mut Vec<Child>) -> PyResult<()> {
    if obj.is_none() {
        return Ok(());
    }
    if let Ok(s) = obj.cast::<PyString>() {
        out.push(Child::Text(s.to_string()));
    } else if let Ok(el) = obj.extract::<PyRef<'_, PyElement>>() {
        out.push(Child::Node(el.inner.clone()));
    } else if let Ok(frag) = obj.extract::<PyRef<'_, Fragment>>() {
        out.push(Child::Fragment(frag.children.clone()));
    } else if let Ok(raw) = obj.extract::<PyRef<'_, Raw>>() {
        out.push(Child::Raw(raw.0.clone()));
    } else if let Ok(style) = obj.extract::<PyRef<'_, PyStyle>>() {
        let css = render_stylesheet(&style.items);
        out.push(Child::Raw(format!("<style>{css}</style>")));
    } else if let Ok(script) = obj.extract::<PyRef<'_, PyScript>>() {
        let mut s = String::from("<script");
        for (name, value) in &script.element.attrs {
            match value {
                AttrValue::String(v) => {
                    s.push(' ');
                    s.push_str(name);
                    s.push_str("=\"");
                    s.push_str(v);
                    s.push('"');
                }
                AttrValue::Bool(true) => {
                    s.push(' ');
                    s.push_str(name);
                }
                AttrValue::Bool(false) => {}
            }
        }
        s.push('>');
        if !script.items.is_empty() {
            s.push_str(&render_script(&script.items));
        }
        s.push_str("</script>");
        out.push(Child::Raw(s));
    } else if let Ok(list) = obj.cast::<PyList>() {
        for item in list.iter() {
            collect_child(&item, out)?;
        }
    } else if obj.is_instance_of::<pyo3::types::PyInt>() || obj.is_instance_of::<PyFloat>() {
        out.push(Child::Text(obj.str()?.to_string()));
    } else if obj.hasattr("__ztml_render__")? {
        let result = obj.call_method0("__ztml_render__")?;
        collect_child(&result, out)?;
    } else {
        return Err(pyo3::exceptions::PyTypeError::new_err(format!(
            "Cannot use {} as a child element",
            obj.get_type().name()?
        )));
    }
    Ok(())
}
