"""Render the English PMPP site into Chinese and bilingual versions.

Translations are structured data, never edited HTML: `extract()` turns a page
into plain-text nodes with placeholders standing in for markup, and `render()`
puts the structure back deterministically, refusing to emit a page that fails
any of its checks.

This package must never import the site builder — the dependency runs the other
way, so rebuilding the English site from the EPUB cannot lose translations.
"""
from .glossary import load_glossary
from .render import RenderResult, extract, render
from .validate import Violation

__all__ = ["RenderResult", "Violation", "extract", "load_glossary", "render"]
