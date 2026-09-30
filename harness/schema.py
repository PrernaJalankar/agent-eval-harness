from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
import yaml
from pathlib import Path


class Case(BaseModel):
    id: str
    input: str
    reference: str | None = None
    rubric: str | None = None
    tags: list[str] = []
    expected_tools: list[str] = []
    forbidden_tools: list[str] = []
    must_contain: list[str] = []
    must_not_contain: list[str] = []
    max_tool_calls: int = 8
    # later weeks will add these:
    relevant_docs: list[str] = []
    arg_checks: list[dict] = []


class RunResult(BaseModel):
    answer: str = ""
    tool_calls: list[dict] = []          # [{"name": ..., "args": {...}}]
    retrieved: list[str] = []
    contexts: list[str] = []
    latency_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    error: str = ""
    events: list[dict] = []

    @property
    def tool_names(self) -> list[str]:
        return [c["name"] for c in self.tool_calls]


def load_cases(path: str | Path) -> list[Case]:
    data = yaml.safe_load(Path(path).read_text())
    if isinstance(data, dict) and "cases" in data:
        data = data["cases"]
    return [Case(**c) for c in data]
