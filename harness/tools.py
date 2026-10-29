from __future__ import annotations
import re
from langchain_core.tools import tool
from harness.retriever import retrieve


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple math expression. Only supports +, -, *, /, parentheses, numbers."""
    allowed = re.compile(r"^[\d\s\+\-\*\/\(\)\.]+$")
    if not allowed.match(expression):
        return "Error: unsupported characters"
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"


@tool
def search_docs(query: str) -> str:
    """Search the documentation corpus and return the best matching passages."""
    hits = retrieve(query, k=4)
    if not hits:
        return "no results"
    return "\n---\n".join(f"[[doc:{h['doc']}]] {h['text']}" for h in hits)
