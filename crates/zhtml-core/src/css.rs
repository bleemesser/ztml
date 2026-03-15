use indexmap::IndexMap;

/// Most abstract representation of any CSS that can appear in a `<style>` block
#[derive(Debug, Clone)]
pub enum CssItem {
    Rule(CssRule),
    Media(MediaQuery),
    Keyframes(Keyframes),
    Raw(String), // to bypass our generation or insert custom CSS
}

/// CSS rule: selector string + property:value map
#[derive(Debug, Clone)]
pub struct CssRule {
    pub selector: String,
    pub properties: IndexMap<String, String>,
}

impl CssRule {
    /// Create a new CSS rule with no properties
    pub fn new(selector: impl Into<String>) -> Self {
        Self {
            selector: selector.into(),
            properties: IndexMap::new(),
        }
    }

    /// Set a CSS property in the map (overwriting existing value if set)
    pub fn set_property(&mut self, name: impl Into<String>, value: impl Into<String>) {
        self.properties.insert(name.into(), value.into());
    }
}

/// `@media` query that wraps some rules
#[derive(Debug, Clone)]
pub struct MediaQuery {
    pub query: String,
    pub rules: Vec<CssRule>,
}

/// `@keyframes` animation definition with a name and step sequence
#[derive(Debug, Clone)]
pub struct Keyframes {
    pub name: String,
    pub steps: Vec<KeyframeStep>,
}

/// A single step in an `@keyfrmames` animation (i.e. `from`, `to`, etc.)
#[derive(Debug, Clone)]
pub struct KeyframeStep {
    pub selector: String,
    pub properties: IndexMap<String, String>,
}

impl KeyframeStep {
    /// Create a new keyframe step with no properties
    pub fn new(selector: impl Into<String>) -> Self {
        Self {
            selector: selector.into(),
            properties: IndexMap::new(),
        }
    }

    /// Set a CSS property on this keyframe step
    pub fn set_property(&mut self, name: impl Into<String>, value: impl Into<String>) {
        self.properties.insert(name.into(), value.into());
    }
}
