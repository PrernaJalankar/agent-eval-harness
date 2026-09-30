from __future__ import annotations
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
import time


class TraceCollector(BaseCallbackHandler):
    """Simple callback that records tokens, latency and tool calls."""

    def __init__(self):
        self.start: float | None = None
        self.input_tokens = 0
        self.output_tokens = 0
        self.tool_calls: list[dict] = []
        self.events: list[dict] = []

    def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], **kwargs) -> None:
        if self.start is None:
            self.start = time.time()

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        # Try to read token usage from the response
        try:
            usage = response.llm_output.get("token_usage") or {}
            self.input_tokens += usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0)
            self.output_tokens += usage.get("completion_tokens", 0) or usage.get("output_tokens", 0)
        except Exception:
            pass

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs) -> None:
        name = serialized.get("name", "unknown")
        self.events.append({"type": "tool_start", "name": name, "input": input_str})

    def on_tool_end(self, output: str, **kwargs) -> None:
        self.events.append({"type": "tool_end", "output": str(output)[:200]})

    @property
    def latency_s(self) -> float:
        if self.start is None:
            return 0.0
        return time.time() - self.start
