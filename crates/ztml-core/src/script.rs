/// Most abstract representation of any content in a `<script>` tag
#[derive(Debug, Clone)]
pub enum ScriptItem {
    Handler(EventHandler),
    Raw(String),
}

/// Container for a DOM event handler: event name, CSS selector, and JS body
#[derive(Debug, Clone)]
pub struct EventHandler {
    pub event: String,
    pub selector: String,
    pub js: String,
}

impl EventHandler {
    /// Create an event handler that fires `js` when `event` happens on any elements matching `selector`
    pub fn new(
        event: impl Into<String>,
        selector: impl Into<String>,
        js: impl Into<String>,
    ) -> Self {
        Self {
            event: event.into(),
            selector: selector.into(),
            js: js.into(),
        }
    }

    /// Creates a `DOMContentLoaded` handler that fires `js` when the document is ready
    pub fn document_ready(js: impl Into<String>) -> Self {
        Self {
            event: "DOMContentLoaded".into(),
            selector: String::new(),
            js: js.into(),
        }
    }
}
