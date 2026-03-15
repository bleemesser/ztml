//! Generated HTML element factory functions.
//! Built from webtags.json by build.rs — do not edit manually.

#![allow(non_snake_case)]

use pyo3::prelude::*;
use pyo3_stub_gen::derive::gen_stub_pyfunction;

use crate::overrides::{py_to_children, PyElement};

/// Macro for defining element factory functions. Used by generated code.
macro_rules! element_fn {
    ($fn_name:ident, $tag:expr, $self_closing:expr) => {
        #[gen_stub_pyfunction]
        #[pyfunction]
        #[pyo3(signature = (*args))]
        pub fn $fn_name(args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<PyElement> {
            let children = py_to_children(args)?;
            Ok(PyElement::create($tag, $self_closing, children))
        }
    };
}

include!(concat!(env!("OUT_DIR"), "/generated_elements.rs"));
