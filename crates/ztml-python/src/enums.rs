//! Generated enum classes for CSS property keywords and HTML attribute values.
//! Built from w3c/webref and webtags.json by build.rs — do not edit manually.

#![allow(non_snake_case, non_camel_case_types)]

use pyo3::prelude::*;
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};

// Generated CSS enum classes (Display, Position, FlexDirection, etc.)
include!(concat!(env!("OUT_DIR"), "/generated_css_enums.rs"));

// Generated HTML attribute enum classes (InputType, ButtonType, etc.)
include!(concat!(env!("OUT_DIR"), "/generated_html_enums.rs"));

/// Register all generated enum classes on the Python module.
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    register_css_enums(m)?;
    register_html_enums(m)?;
    Ok(())
}
