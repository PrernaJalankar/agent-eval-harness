from langchain_core.tools import tool
import re
from pathlib import Path


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


def _load_corpus() -> dict[str, str]:
    docs = {}
    corpus = Path("corpus")
    if not corpus.exists():
        return docs
    for p in corpus.glob("*"):
        if p.is_file():
            docs[p.name] = p.read_text(errors="ignore")
    return docs


@tool
def search_docs(query: str) -> str:
    """Search the documentation corpus and return the best matching passages."""
    docs = _load_corpus()
    if not docs:
        return "no results"
    q = query.lower()
    hits = []
    for name, text in docs.items():
        if any(w in text.lower() for w in q.split() if len(w) > 2):
            hits.append(f"[[doc:{name}]] {text[:600]}")
    if not hits:
        return "no results"
    return "\n---\n".join(hits[:4])
