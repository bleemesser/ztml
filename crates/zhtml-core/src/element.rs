use indexmap::IndexMap;

/// Most abstracted HTML element representation: tag + attributes + children
#[derive(Debug, Clone)]
pub struct Element {
    /// Tag name
    pub tag: String,
    /// Map of attributes, i.e. `src: "http://..."` or `visible: true`
    pub attrs: IndexMap<String, AttrValue>,
    /// Whatever content is stored within the element, i.e. the text inside a `<p>[...]</p>` or any nested stuff
    pub children: Vec<Child>,
    /// Some html elements like `<br>` do not have closing tags
    pub self_closing: bool,
}

/// An HTML attribute: either a string or a bool
#[derive(Debug, Clone)]
pub enum AttrValue {
    String(String),
    Bool(bool),
}

/// A child node in an HTML tree
#[derive(Debug, Clone)]
pub enum Child {
    /// Text content that is automatically HTML-escaped on render
    Text(String),
    /// Raw HTML content or other string, inserted with NO ESCAPING!!
    Raw(String),
    /// A nested HTML element
    Node(Element),
    /// A list of children rendered without a parent/wrapper element
    Fragment(Vec<Child>),
}

impl Element {
    /// Create a new element with no attrs
    pub fn new(tag: impl Into<String>, self_closing: bool) -> Self {
        Self {
            tag: tag.into(),
            attrs: IndexMap::new(),
            children: Vec::new(),
            self_closing,
        }
    }

    /// Set an attribute on the element, overwriting any previous value for that key
    pub fn set_attr(&mut self, name: impl Into<String>, value: AttrValue) {
        self.attrs.insert(name.into(), value);
    }

    /// Push a CSS clas to the `class` attribute.
    /// Special case of `set_attr` for class names, since multiple classes are
    /// specifiable with spaces in between.
    ///
    /// Automatically ignores empty strings.
    pub fn append_class(&mut self, class: &str) {
        if class.is_empty() {
            return;
        }
        let key = "class".to_string();
        match self.attrs.get(&key) {
            Some(AttrValue::String(existing)) => {
                let new = format!("{existing} {class}");
                self.attrs.insert(key, AttrValue::String(new));
            }
            _ => {
                self.attrs.insert(key, AttrValue::String(class.to_string()));
            }
        }
    }

    /// Append a child node to this element
    pub fn add_child(&mut self, child: Child) {
        self.children.push(child);
    }
}
