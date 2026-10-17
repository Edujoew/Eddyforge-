import re
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit

import markdown
from django.utils.safestring import mark_safe


ALLOWED_TAGS = {
    "a", "blockquote", "br", "code", "del", "div", "em", "h1", "h2", "h3",
    "h4", "h5", "h6", "hr", "img", "li", "ol", "p", "pre", "span", "strong",
    "table", "tbody", "td", "th", "thead", "tr", "ul",
}
VOID_TAGS = {"br", "hr", "img"}
DROP_CONTENT_TAGS = {"iframe", "object", "script", "style", "svg"}


def safe_url(value):
    parsed = urlsplit(value.strip())
    if parsed.scheme:
        return parsed.scheme.lower() in {"http", "https", "mailto"}
    return not value.lstrip().startswith("//")


class MarkdownHTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.parts = []
        self.open_tags = []
        self.dropped = []

    def handle_starttag(self, tag, attrs):
        if self.dropped:
            if tag in DROP_CONTENT_TAGS:
                self.dropped.append(tag)
            return
        if tag in DROP_CONTENT_TAGS:
            self.dropped.append(tag)
            return
        safe_tag = "h2" if tag == "h1" else tag
        if safe_tag not in ALLOWED_TAGS:
            return

        safe_attrs = []
        attributes = dict(attrs)
        if tag == "a" and attributes.get("href") and safe_url(attributes["href"]):
            safe_attrs.append(("href", attributes["href"]))
            safe_attrs.append(("rel", "noopener noreferrer"))
        if safe_tag in {"h2", "h3", "h4", "h5", "h6"}:
            identifier = attributes.get("id", "")
            if re.fullmatch(r"[A-Za-z0-9_.:-]+", identifier):
                safe_attrs.append(("id", identifier))
        class_value = attributes.get("class", "")
        class_tokens = [
            token
            for token in class_value.split()
            if re.fullmatch(r"[A-Za-z0-9_-]+", token)
        ]
        if class_tokens and tag in {"code", "div", "span"}:
            safe_attrs.append(("class", " ".join(class_tokens)))
        if tag == "img":
            src = attributes.get("src", "")
            if src and safe_url(src):
                safe_attrs.append(("src", src))
                safe_attrs.append(("alt", attributes.get("alt", "")))
                safe_attrs.append(("loading", "lazy"))
            else:
                return
        for attribute in ("colspan", "rowspan"):
            value = attributes.get(attribute, "")
            if tag in {"td", "th"} and value.isdigit() and 1 <= int(value) <= 20:
                safe_attrs.append((attribute, value))
        rendered = "".join(
            f' {name}="{escape(value, quote=True)}"' for name, value in safe_attrs
        )
        self.parts.append(f"<{safe_tag}{rendered}>")
        if safe_tag not in VOID_TAGS:
            self.open_tags.append(safe_tag)

    def handle_endtag(self, tag):
        if self.dropped:
            if tag == self.dropped[-1]:
                self.dropped.pop()
            return
        if tag == "h1":
            tag = "h2"
        if tag not in self.open_tags:
            return
        while self.open_tags:
            opened = self.open_tags.pop()
            self.parts.append(f"</{opened}>")
            if opened == tag:
                break

    def handle_data(self, data):
        if not self.dropped:
            self.parts.append(escape(data))

    def handle_entityref(self, name):
        if not self.dropped and re.fullmatch(r"[A-Za-z0-9]+", name):
            self.parts.append(f"&{name};")

    def handle_charref(self, name):
        if not self.dropped and re.fullmatch(r"x?[A-Fa-f0-9]+", name):
            self.parts.append(f"&#{name};")

    def handle_comment(self, data):
        return


def render_markdown(source):
    rendered = markdown.markdown(source, extensions=["fenced_code", "tables", "toc"])
    sanitizer = MarkdownHTMLSanitizer()
    sanitizer.feed(rendered)
    sanitizer.close()
    while sanitizer.open_tags:
        sanitizer.parts.append(f"</{sanitizer.open_tags.pop()}>")
    return mark_safe("".join(sanitizer.parts))
