use pyo3::prelude::*;
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};
use zhtml_core::element::{AttrValue, Element};
use zhtml_core::script::{EventHandler, ScriptItem};

/// Top-level `<script>` container accepting `EventHandler` or `Raw` JS items
#[gen_stub_pyclass]
#[pyclass(name = "Script")]
pub struct PyScript {
    pub items: Vec<ScriptItem>,
    pub element: Element,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyScript {
    #[new]
    #[pyo3(signature = (*args))]
    fn new(args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<Self> {
        let mut items = Vec::new();
        for arg in args.iter() {
            if let Ok(handler) = arg.extract::<PyRef<'_, PyEventHandler>>() {
                items.push(ScriptItem::Handler(handler.inner.clone()));
            } else if let Ok(raw) = arg.extract::<PyRef<'_, PyRawJs>>() {
                items.push(ScriptItem::Raw(raw.0.clone()));
            } else {
                return Err(pyo3::exceptions::PyTypeError::new_err(
                    "Script() accepts EventHandler or RawJs",
                ));
            }
        }
        Ok(Self {
            items,
            element: Element::new("script", false),
        })
    }

    /// Set the `src` attribute
    fn src(mut slf: PyRefMut<'_, Self>, url: String) -> PyRefMut<'_, Self> {
        slf.element.set_attr("src", AttrValue::String(url));
        slf
    }

    /// Set the `defer` attribute
    #[pyo3(signature = (value=true))]
    fn defer(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.element.set_attr("defer", AttrValue::Bool(value));
        slf
    }

    /// Set the `async` attribute (named `async_` because `async` is a Rust keyword)
    #[pyo3(signature = (value=true))]
    fn async_(mut slf: PyRefMut<'_, Self>, value: bool) -> PyRefMut<'_, Self> {
        slf.element.set_attr("async", AttrValue::Bool(value));
        slf
    }

    /// Set the `type` attribute
    #[pyo3(name = "type")]
    fn type_(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.element.set_attr("type", AttrValue::String(value));
        slf
    }

    /// Set the `crossorigin` attribute
    fn crossorigin(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.element.set_attr("crossorigin", AttrValue::String(value));
        slf
    }

    /// Set the `integrity` attribute for subresource integrity checks
    fn integrity(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.element.set_attr("integrity", AttrValue::String(value));
        slf
    }
}

/// Factory with static methods for common DOM event handlers
#[gen_stub_pyclass]
#[pyclass(name = "On")]
pub struct PyOn;

#[gen_stub_pymethods]
#[pymethods]
impl PyOn {
    /// Fire JS when the document is ready (`DOMContentLoaded`)
    #[staticmethod]
    fn document_ready(js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::document_ready(js) }
    }
    /// Fire JS on `click` events matching `selector`
    #[staticmethod]
    fn click(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("click", selector, js) }
    }
    /// Fire JS on `submit` events matching `selector`
    #[staticmethod]
    fn submit(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("submit", selector, js) }
    }
    /// Fire JS on `change` events matching `selector`
    #[staticmethod]
    fn change(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("change", selector, js) }
    }
    /// Fire JS on `input` events matching `selector`
    #[staticmethod]
    fn input(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("input", selector, js) }
    }
    /// Fire JS on `keydown` events matching `selector`
    #[staticmethod]
    fn keydown(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("keydown", selector, js) }
    }
    /// Fire JS on `keyup` events matching `selector`
    #[staticmethod]
    fn keyup(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("keyup", selector, js) }
    }
    /// Fire JS on `mouseover` events matching `selector`
    #[staticmethod]
    fn mouseover(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("mouseover", selector, js) }
    }
    /// Fire JS on `mouseout` events matching `selector`
    #[staticmethod]
    fn mouseout(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("mouseout", selector, js) }
    }
    /// Fire JS on `focus` events matching `selector`
    #[staticmethod]
    fn focus(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("focus", selector, js) }
    }
    /// Fire JS on `blur` events matching `selector`
    #[staticmethod]
    fn blur(selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new("blur", selector, js) }
    }
    /// Fire JS on any named event matching `selector`
    #[staticmethod]
    fn event(name: &str, selector: &str, js: &str) -> PyEventHandler {
        PyEventHandler { inner: EventHandler::new(name, selector, js) }
    }
}

/// Wrap a core `EventHandler` for Python exposure
#[gen_stub_pyclass]
#[pyclass(name = "EventHandler", skip_from_py_object)]
#[derive(Clone)]
pub struct PyEventHandler {
    pub inner: EventHandler,
}

/// Raw JavaScript text injected verbatim into a `<script>` block
#[gen_stub_pyclass]
#[pyclass(name = "RawJs", skip_from_py_object)]
#[derive(Clone)]
pub struct PyRawJs(pub String);

#[gen_stub_pymethods]
#[pymethods]
impl PyRawJs {
    #[new]
    fn new(text: &str) -> Self {
        Self(text.to_string())
    }
}

/// Register all script-related classes on the Python module
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyScript>()?;
    m.add_class::<PyOn>()?;
    m.add_class::<PyEventHandler>()?;
    m.add_class::<PyRawJs>()?;
    Ok(())
}
