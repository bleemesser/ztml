//! Build script that reads committed HTML/CSS specs and generates PyO3 element functions,
//! CSS property methods, and enum class definitions.
//!
//! Specs live in `<workspace>/specs/` and are checked into version control.

use serde::Deserialize;
use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::io::Write;
use std::path::{Path, PathBuf};

/// Void (self-closing) HTML elements.
const VOID_ELEMENTS: &[&str] = &[
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source",
    "track", "wbr",
];

/// Elements to skip (we handle <script> and <style> specially via Script/Style classes).
const SKIP_ELEMENTS: &[&str] = &["script", "style"];

fn main() {
    let manifest_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
    let workspace_root = manifest_dir.parent().unwrap().parent().unwrap();
    let specs_dir = workspace_root.join("specs");

    let out_dir = PathBuf::from(std::env::var("OUT_DIR").unwrap());

    let webtags_path = specs_dir.join("webtags.json");
    let css_dir = specs_dir.join("css");

    let mut elements_file = fs::File::create(out_dir.join("generated_elements.rs")).unwrap();
    generate_elements(&webtags_path, &mut elements_file);

    let mut css_methods_file = fs::File::create(out_dir.join("generated_css_methods.rs")).unwrap();
    let mut css_enums_file = fs::File::create(out_dir.join("generated_css_enums.rs")).unwrap();
    generate_css(&css_dir, &mut css_methods_file, &mut css_enums_file);

    let mut html_enums_file = fs::File::create(out_dir.join("generated_html_enums.rs")).unwrap();
    generate_html_enums(&webtags_path, &mut html_enums_file);

    println!("cargo:rerun-if-changed=build.rs");
    println!(
        "cargo:rerun-if-changed={}",
        specs_dir.join("webtags.json").display()
    );
    println!("cargo:rerun-if-changed={}", css_dir.display());
}

fn generate_elements(webtags_path: &Path, out: &mut impl Write) {
    let text = fs::read_to_string(webtags_path).unwrap();
    let webtags: WebTags = serde_json::from_str(&text).unwrap();

    // Find the HTML spec
    let html_spec = webtags
        .specs
        .iter()
        .find(|s| s.shortname == "html")
        .expect("HTML spec not found in webtags.json");

    let mut element_names = Vec::new();

    for el in &html_spec.elements {
        if el.obsolete || SKIP_ELEMENTS.contains(&el.name.as_str()) {
            continue;
        }
        let self_closing = VOID_ELEMENTS.contains(&el.name.as_str());
        let fn_name = pascal_case(&el.name);

        // <option> needs special handling (`Option` is a Rust built-in)
        if fn_name == "Option" {
            writeln!(out, r#"#[gen_stub_pyfunction]"#).unwrap();
            writeln!(out, r#"#[pyfunction(name = "Option")]"#).unwrap();
            writeln!(out, r#"#[pyo3(signature = (*args))]"#).unwrap();
            writeln!(
                out,
                r#"pub fn HtmlOption(args: &Bound<'_, pyo3::types::PyTuple>) -> PyResult<PyElement> {{"#
            )
            .unwrap();
            writeln!(out, r#"    let children = py_to_children(args)?;"#).unwrap();
            writeln!(
                out,
                r#"    Ok(PyElement::create({:?}, {}, children))"#,
                el.name, self_closing
            )
            .unwrap();
            writeln!(out, r#"}}"#).unwrap();
            element_names.push("HtmlOption".to_string());
        } else {
            writeln!(
                out,
                r#"element_fn!({fn_name}, {:?}, {self_closing});"#,
                el.name
            )
            .unwrap();
            element_names.push(fn_name);
        }
    }

    writeln!(out).unwrap();
    writeln!(
        out,
        "pub fn register_elements(m: &Bound<'_, pyo3::prelude::PyModule>) -> PyResult<()> {{"
    )
    .unwrap();
    for name in &element_names {
        writeln!(
            out,
            "    m.add_function(pyo3::wrap_pyfunction!({name}, m)?)?;"
        )
        .unwrap();
    }
    writeln!(out, "    Ok(())").unwrap();
    writeln!(out, "}}").unwrap();
}

fn generate_css(css_dir: &Path, out_methods: &mut impl Write, out_enums: &mut impl Write) {
    // Aggregate all CSS properties across all spec files
    let mut all_properties: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();

    // Manual overrides: the w3c/webref specs define keyword values in the syntax
    // string (e.g. "flex | inline-flex | grid") but not always in the structured
    // `values` array. We inject the most commonly used keywords here.
    let overrides: &[(&str, &[&str])] = &[
        (
            "display",
            &["flex", "inline-flex", "grid", "inline-grid", "contents"],
        ),
        (
            "position",
            &["static", "relative", "absolute", "fixed", "sticky"],
        ),
        ("overflow", &["visible", "hidden", "scroll", "auto", "clip"]),
        ("visibility", &["visible", "hidden", "collapse"]),
        ("box-sizing", &["content-box", "border-box"]),
        (
            "float",
            &["left", "right", "none", "inline-start", "inline-end"],
        ),
        (
            "clear",
            &[
                "left",
                "right",
                "both",
                "none",
                "inline-start",
                "inline-end",
            ],
        ),
        (
            "cursor",
            &[
                "auto",
                "default",
                "none",
                "context-menu",
                "help",
                "pointer",
                "progress",
                "wait",
                "cell",
                "crosshair",
                "text",
                "vertical-text",
                "alias",
                "copy",
                "move",
                "no-drop",
                "not-allowed",
                "grab",
                "grabbing",
                "col-resize",
                "row-resize",
                "n-resize",
                "e-resize",
                "s-resize",
                "w-resize",
                "nesw-resize",
                "nwse-resize",
                "zoom-in",
                "zoom-out",
            ],
        ),
        (
            "flex-direction",
            &["row", "row-reverse", "column", "column-reverse"],
        ),
        ("flex-wrap", &["nowrap", "wrap", "wrap-reverse"]),
        (
            "justify-content",
            &[
                "flex-start",
                "flex-end",
                "center",
                "space-between",
                "space-around",
                "space-evenly",
            ],
        ),
        (
            "align-items",
            &["stretch", "flex-start", "flex-end", "center", "baseline"],
        ),
        (
            "align-self",
            &[
                "auto",
                "stretch",
                "flex-start",
                "flex-end",
                "center",
                "baseline",
            ],
        ),
        (
            "text-align",
            &["left", "right", "center", "justify", "start", "end"],
        ),
        (
            "text-decoration-line",
            &["none", "underline", "overline", "line-through"],
        ),
        (
            "text-transform",
            &["none", "capitalize", "uppercase", "lowercase", "full-width"],
        ),
        (
            "white-space",
            &[
                "normal",
                "nowrap",
                "pre",
                "pre-wrap",
                "pre-line",
                "break-spaces",
            ],
        ),
        ("font-weight", &["normal", "bold", "bolder", "lighter"]),
        ("font-style", &["normal", "italic", "oblique"]),
        (
            "border-style",
            &[
                "none", "hidden", "dotted", "dashed", "solid", "double", "groove", "ridge",
                "inset", "outset",
            ],
        ),
    ];

    for (prop, vals) in overrides {
        let entry = all_properties.entry(prop.to_string()).or_default();
        for v in *vals {
            entry.insert(v.to_string());
        }
    }

    for entry in fs::read_dir(css_dir).unwrap() {
        let entry = entry.unwrap();
        if !entry.path().extension().map_or(false, |e| e == "json") {
            continue;
        }
        let text = fs::read_to_string(entry.path()).unwrap();
        let spec: CssSpec = match serde_json::from_str(&text) {
            Ok(s) => s,
            Err(_) => continue,
        };

        for prop in &spec.properties {
            // Skip vendor-prefixed and internal properties
            if prop.name.starts_with('-') || prop.name.starts_with("--") {
                continue;
            }
            let entry = all_properties.entry(prop.name.clone()).or_default();
            for val in &prop.values {
                if val.value_type == "value" && !val.name.starts_with('<') {
                    // Only plain keyword values, not type references
                    entry.insert(val.name.clone());
                }
            }
        }
    }

    // Generate complete #[pymethods] impl blocks for each CSS type.
    // PyO3 supports multiple #[pymethods] blocks per type.
    let types = [
        ("PyRuleBuilder", "properties"),
        ("PyInlineStyle", "properties"),
        ("PyFrame", "properties"),
    ];
    for (type_name, field_name) in &types {
        writeln!(out_methods, "#[gen_stub_pymethods]").unwrap();
        writeln!(out_methods, "#[pymethods]").unwrap();
        writeln!(out_methods, "impl {type_name} {{").unwrap();
        for prop_name in all_properties.keys() {
            let method_name = rust_safe_name(&snake_case(prop_name));
            if !is_valid_ident(&method_name) {
                continue;
            }
            writeln!(
                out_methods,
                r#"    fn {method_name}(mut slf: PyRefMut<'_, Self>, v: String) -> PyRefMut<'_, Self> {{ slf.{field_name}.insert("{prop_name}".into(), v); slf }}"#
            ).unwrap();
        }
        // prop() escape hatch
        writeln!(
            out_methods,
            r#"    fn prop(mut slf: PyRefMut<'_, Self>, name: String, value: String) -> PyRefMut<'_, Self> {{ slf.{field_name}.insert(name, value); slf }}"#
        ).unwrap();
        writeln!(out_methods, "}}").unwrap();
        writeln!(out_methods).unwrap();
    }

    // Generate CSS enum classes for properties that have keyword values
    for (prop_name, values) in &all_properties {
        if values.len() < 2 {
            continue;
        }
        // Skip properties whose keywords are too generic (e.g. "auto", "none" only)
        let class_name = pascal_case(prop_name);

        writeln!(out_enums, "#[gen_stub_pyclass]").unwrap();
        writeln!(
            out_enums,
            "#[pyclass(name = \"{class_name}\", skip_from_py_object)]"
        )
        .unwrap();
        writeln!(out_enums, "#[derive(Clone)]").unwrap();
        writeln!(out_enums, "pub struct CssEnum{class_name};").unwrap();
        writeln!(out_enums, "#[gen_stub_pymethods]").unwrap();
        writeln!(out_enums, "#[pymethods]").unwrap();
        writeln!(out_enums, "impl CssEnum{class_name} {{").unwrap();
        for val in values {
            let attr_name = rust_safe_name(&snake_case(val));
            if !is_valid_ident(&attr_name) {
                continue;
            }
            writeln!(
                out_enums,
                "    #[classattr] fn {attr_name}() -> String {{ {:?}.into() }}",
                val
            )
            .unwrap();
        }
        writeln!(out_enums, "}}").unwrap();
        writeln!(out_enums).unwrap();
    }

    // Generate register function for CSS enums
    writeln!(
        out_enums,
        "pub fn register_css_enums(m: &Bound<'_, pyo3::prelude::PyModule>) -> pyo3::PyResult<()> {{"
    )
    .unwrap();
    for (prop_name, values) in &all_properties {
        if values.len() < 2 {
            continue;
        }
        let class_name = pascal_case(prop_name);
        writeln!(out_enums, "    m.add_class::<CssEnum{class_name}>()?;").unwrap();
    }
    writeln!(out_enums, "    Ok(())").unwrap();
    writeln!(out_enums, "}}").unwrap();

    // Generate a count constant for reference
    writeln!(
        out_methods,
        "\n// Generated {} CSS property methods",
        all_properties.len()
    )
    .unwrap();
}

fn generate_html_enums(webtags_path: &Path, out: &mut impl Write) {
    let text = fs::read_to_string(webtags_path).unwrap();
    let webtags: WebTags = serde_json::from_str(&text).unwrap();

    let html_spec = webtags
        .specs
        .iter()
        .find(|s| s.shortname == "html")
        .expect("HTML spec not found");

    // Collect all attribute enums across all elements
    let mut attr_enums: BTreeMap<String, BTreeSet<String>> = BTreeMap::new();

    for el in &html_spec.elements {
        if el.obsolete {
            continue;
        }
        for attr in &el.attributes {
            if attr.obsolete || attr.values.is_empty() {
                continue;
            }
            let values: BTreeSet<String> = attr
                .values
                .iter()
                .filter(|v| !v.obsolete)
                .map(|v| v.value.clone())
                .collect();
            if values.len() >= 2 {
                // Use element_name + attr_name for uniqueness, but common attrs merge
                let key = format!("{}{}", pascal_case(&el.name), pascal_case(&attr.name));
                let entry = attr_enums.entry(key).or_default();
                entry.extend(values);
            }
        }
    }

    // Only generate enums for the most useful ones — those used by multiple elements
    // or that are commonly needed. For now generate all with 2+ values.
    for (enum_name, values) in &attr_enums {
        writeln!(out, "#[gen_stub_pyclass]").unwrap();
        writeln!(
            out,
            "#[pyclass(name = \"{enum_name}\", skip_from_py_object)]"
        )
        .unwrap();
        writeln!(out, "#[derive(Clone)]").unwrap();
        writeln!(out, "pub struct HtmlEnum{enum_name};").unwrap();
        writeln!(out, "#[gen_stub_pymethods]").unwrap();
        writeln!(out, "#[pymethods]").unwrap();
        writeln!(out, "impl HtmlEnum{enum_name} {{").unwrap();
        for val in values {
            let attr_name = rust_safe_name(&snake_case(val));
            if !is_valid_ident(&attr_name) {
                continue;
            }
            writeln!(
                out,
                "    #[classattr] fn {attr_name}() -> String {{ {:?}.into() }}",
                val
            )
            .unwrap();
        }
        writeln!(out, "}}").unwrap();
        writeln!(out).unwrap();
    }

    // Register function
    writeln!(
        out,
        "pub fn register_html_enums(m: &Bound<'_, pyo3::prelude::PyModule>) -> pyo3::PyResult<()> {{"
    )
    .unwrap();
    for enum_name in attr_enums.keys() {
        writeln!(out, "    m.add_class::<HtmlEnum{enum_name}>()?;").unwrap();
    }
    writeln!(out, "    Ok(())").unwrap();
    writeln!(out, "}}").unwrap();
}

/// Rust/Python keywords that need renaming when used as identifiers.
fn rust_safe_name(name: &str) -> String {
    let base = name.replace('-', "_");
    match base.as_str() {
        "type" | "for" | "as" | "async" | "loop" | "match" | "move" | "ref" | "return"
        | "self" | "static" | "super" | "yield" | "in" | "where" | "continue" | "break"
        | "fn" | "let" | "mut" | "pub" | "use" | "mod" | "if" | "else" | "while" | "true"
        | "false" | "struct" | "enum" | "impl" | "trait" | "const" | "crate" | "extern"
        | "unsafe" | "dyn" | "abstract" | "become" | "box" | "do" | "final" | "macro"
        | "override" | "priv" | "typeof" | "unsized" | "virtual" | "try" | "union"
        // Python keywords
        | "None" | "True" | "False" | "class" | "def" | "del" | "from" | "global"
        | "import" | "is" | "lambda" | "not" | "or" | "and" | "pass" | "raise" | "with" => {
            format!("{base}_")
        }
        _ => base,
    }
}

/// Returns true if a string is a valid Rust identifier (alphanumeric + underscore, not starting with digit).
fn is_valid_ident(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }
    let first = s.chars().next().unwrap();
    if !first.is_ascii_alphabetic() && first != '_' {
        return false;
    }
    s.chars().all(|c| c.is_ascii_alphanumeric() || c == '_')
}

/// Convert a tag name like "div" to a PascalCase struct name like "Div".
fn pascal_case(s: &str) -> String {
    s.split('-')
        .map(|part| {
            let mut chars = part.chars();
            match chars.next() {
                None => String::new(),
                Some(c) => c.to_uppercase().to_string() + &chars.as_str().to_lowercase(),
            }
        })
        .collect()
}

/// Convert a CSS property/value name to snake_case.
/// Replaces hyphens and spaces with underscores, strips non-alphanumeric chars.
fn snake_case(s: &str) -> String {
    s.replace('-', "_")
        .replace(' ', "_")
        .replace(|c: char| !c.is_ascii_alphanumeric() && c != '_', "")
}

#[derive(Deserialize)]
struct WebTags {
    specs: Vec<WebTagsSpec>,
}

#[derive(Deserialize)]
struct WebTagsSpec {
    shortname: String,
    elements: Vec<WebTagsElement>,
    #[serde(rename = "globalAttributes", default)]
    _global_attributes: Vec<WebTagsAttr>,
}

#[derive(Deserialize)]
struct WebTagsElement {
    name: String,
    #[serde(default)]
    obsolete: bool,
    #[serde(default)]
    attributes: Vec<WebTagsAttr>,
}

#[derive(Deserialize)]
struct WebTagsAttr {
    name: String,
    #[serde(default)]
    obsolete: bool,
    #[serde(default)]
    values: Vec<WebTagsAttrValue>,
}

#[derive(Deserialize)]
struct WebTagsAttrValue {
    value: String,
    #[serde(default)]
    obsolete: bool,
}

#[derive(Deserialize)]
struct CssSpec {
    #[serde(default)]
    properties: Vec<CssProperty>,
}

#[derive(Deserialize)]
struct CssProperty {
    name: String,
    #[serde(default)]
    values: Vec<CssValue>,
}

#[derive(Deserialize)]
struct CssValue {
    name: String,
    #[serde(rename = "type", default)]
    value_type: String,
}
