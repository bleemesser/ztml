#![allow(non_snake_case)]

mod css;
mod elements;
mod enums;
pub mod overrides;
mod render;
mod script;

use pyo3::prelude::*;
use pyo3_stub_gen::StubInfo;

/// Top-level PyO3 module definition.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    overrides::register(m)?;
    elements::register_elements(m)?;
    css::register(m)?;
    script::register(m)?;
    enums::register(m)?;
    m.add_function(pyo3::wrap_pyfunction!(render::render, m)?)?;
    Ok(())
}

/// Gather type information from annotated PyO3 classes/functions for `.pyi` stub generation.
pub fn stub_info() -> pyo3_stub_gen::Result<StubInfo> {
    let manifest_dir: &std::path::Path = env!("CARGO_MANIFEST_DIR").as_ref();
    let pyproject_path = manifest_dir
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .join("pyproject.toml");
    StubInfo::from_pyproject_toml(pyproject_path)
}
