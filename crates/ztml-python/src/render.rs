use pyo3::prelude::*;
use pyo3_stub_gen::derive::gen_stub_pyfunction;
use ztml_core::render::{render_child_into, render_element};

use crate::css::PyStyle;
use crate::overrides::{Fragment, PyElement};
use crate::script::PyScript;

/// Render a Python object (i.e. `Element`, `Fragment`, `Style`, `Script`, or any object with
/// `__ztml_render__`) to an HTML string
#[gen_stub_pyfunction]
#[pyfunction]
pub fn render(obj: &Bound<'_, pyo3::PyAny>) -> PyResult<String> {
    if let Ok(el) = obj.extract::<PyRef<'_, PyElement>>() {
        Ok(render_element(&el.inner))
    } else if let Ok(frag) = obj.extract::<PyRef<'_, Fragment>>() {
        let mut out = String::new();
        for child in &frag.children {
            render_child_into(child, &mut out);
        }
        Ok(out)
    } else if let Ok(style) = obj.extract::<PyRef<'_, PyStyle>>() {
        Ok(style.to_html())
    } else if let Ok(script) = obj.extract::<PyRef<'_, PyScript>>() {
        Ok(script.to_html())
    } else if obj.hasattr("__ztml_render__")? {
        let result = obj.call_method0("__ztml_render__")?;
        render(&result)
    } else {
        Err(pyo3::exceptions::PyTypeError::new_err(format!(
            "Cannot render {}",
            obj.get_type().name()?
        )))
    }
}
