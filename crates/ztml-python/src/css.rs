//! CSS property methods are generated from w3c/webref specs by build.rs.

use indexmap::IndexMap;
use pyo3::prelude::*;
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pymethods};
use ztml_core::css::{CssItem, CssRule, KeyframeStep, Keyframes, MediaQuery};
use ztml_core::render::render_stylesheet;

/// Top-level `<style>` container accepting `Rule`, `Media`, `Keyframes`, or `RawCss` items
#[gen_stub_pyclass]
#[pyclass(name = "Style")]
pub struct PyStyle {
    pub items: Vec<CssItem>,
}

impl PyStyle {
    pub fn to_html(&self) -> String {
        let css = render_stylesheet(&self.items);
        format!("<style>{css}</style>")
    }
}

#[gen_stub_pymethods]
#[pymethods]
impl PyStyle {
    fn __html__(&self) -> String {
        self.to_html()
    }

    fn _repr_html_(&self) -> String {
        self.__html__()
    }

    #[new]
    #[pyo3(signature = (*args))]
    fn new(args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<Self> {
        let mut items = Vec::new();
        for arg in args.iter() {
            if let Ok(rule) = arg.extract::<PyRef<'_, PyRuleBuilder>>() {
                items.push(CssItem::Rule(rule.to_css_rule()));
            } else if let Ok(media) = arg.extract::<PyRef<'_, PyMedia>>() {
                items.push(CssItem::Media(media.inner.clone()));
            } else if let Ok(kf) = arg.extract::<PyRef<'_, PyKeyframes>>() {
                items.push(CssItem::Keyframes(kf.inner.clone()));
            } else if let Ok(raw) = arg.extract::<PyRef<'_, PyRawCss>>() {
                items.push(CssItem::Raw(raw.0.clone()));
            } else {
                return Err(pyo3::exceptions::PyTypeError::new_err(
                    "Style() accepts Rule, Media, Keyframes, or RawCss",
                ));
            }
        }
        Ok(Self { items })
    }
}

/// `@media` query wrapping one or more `Rule` items
#[gen_stub_pyclass]
#[pyclass(name = "Media")]
pub struct PyMedia {
    pub inner: MediaQuery,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyMedia {
    #[new]
    #[pyo3(signature = (query, *args))]
    fn new(query: &str, args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<Self> {
        let mut rules = Vec::new();
        for arg in args.iter() {
            let rule: PyRef<'_, PyRuleBuilder> = arg.extract()?;
            rules.push(rule.to_css_rule());
        }
        Ok(Self {
            inner: MediaQuery { query: query.into(), rules },
        })
    }
}

/// `@keyframes` animation definition with a name and `Frame` steps
#[gen_stub_pyclass]
#[pyclass(name = "Keyframes")]
pub struct PyKeyframes {
    pub inner: Keyframes,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyKeyframes {
    #[new]
    #[pyo3(signature = (name, *args))]
    fn new(name: &str, args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<Self> {
        let mut steps = Vec::new();
        for arg in args.iter() {
            let frame: PyRef<'_, PyFrame> = arg.extract()?;
            steps.push(frame.to_keyframe_step());
        }
        Ok(Self {
            inner: Keyframes { name: name.into(), steps },
        })
    }
}

/// Raw CSS text injected verbatim into a `<style>` block
#[gen_stub_pyclass]
#[pyclass(name = "RawCss", skip_from_py_object)]
#[derive(Clone)]
pub struct PyRawCss(pub String);

#[gen_stub_pymethods]
#[pymethods]
impl PyRawCss {
    #[new]
    fn new(text: &str) -> Self { Self(text.into()) }
}

/// CSS rule builder: selector + accumulated property:value pairs
#[gen_stub_pyclass]
#[pyclass(name = "Rule")]
pub struct PyRuleBuilder {
    pub selector: String,
    pub properties: IndexMap<String, String>,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyRuleBuilder {
    /// Create a new rule for the given CSS selector
    #[new]
    fn new(selector: &str) -> Self {
        Self { selector: selector.into(), properties: IndexMap::new() }
    }
}

impl PyRuleBuilder {
    /// Convert accumulated properties into a `ztml_core::CssRule`
    pub fn to_css_rule(&self) -> CssRule {
        let mut rule = CssRule::new(&self.selector);
        for (k, v) in &self.properties {
            rule.set_property(k, v);
        }
        rule
    }
}

/// Inline style builder: accumulate CSS properties for a `style` attribute
#[gen_stub_pyclass]
#[pyclass(name = "InlineStyle", skip_from_py_object)]
#[derive(Clone)]
pub struct PyInlineStyle {
    pub properties: IndexMap<String, String>,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyInlineStyle {
    #[new]
    fn new() -> Self { Self { properties: IndexMap::new() } }
}

/// Keyframe step builder: selector (i.e. `from`, `50%`) + accumulated properties
#[gen_stub_pyclass]
#[pyclass(name = "Frame")]
pub struct PyFrame {
    pub selector: String,
    pub properties: IndexMap<String, String>,
}

#[gen_stub_pymethods]
#[pymethods]
impl PyFrame {
    /// Create a new keyframe step for the given selector
    #[new]
    fn new(selector: &str) -> Self { Self { selector: selector.into(), properties: IndexMap::new() } }
}

impl PyFrame {
    /// Convert accumulated properties into a `ztml_core::KeyframeStep`
    pub fn to_keyframe_step(&self) -> KeyframeStep {
        let mut step = KeyframeStep::new(&self.selector);
        for (k, v) in &self.properties {
            step.set_property(k, v);
        }
        step
    }
}

// Generated CSS property #[pymethods] impl blocks for PyRuleBuilder, PyInlineStyle, PyFrame
include!(concat!(env!("OUT_DIR"), "/generated_css_methods.rs"));

/// Register CSS structural classes on the Python module
pub fn register(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyStyle>()?;
    m.add_class::<PyMedia>()?;
    m.add_class::<PyKeyframes>()?;
    m.add_class::<PyRawCss>()?;
    m.add_class::<PyRuleBuilder>()?;
    m.add_class::<PyInlineStyle>()?;
    m.add_class::<PyFrame>()?;
    Ok(())
}
