from __future__ import annotations
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from harness.tools import calculator, search_docs

load_dotenv()


def build_agent(model: str | None = None):
    """Build a simple ReAct agent with calculator + search_docs tools."""
    llm = ChatOpenAI(
        model=model or os.getenv("AGENT_MODEL"),
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY"),
        temperature=0,
    )
    tools = [calculator, search_docs]
    system = (
        "You are a helpful assistant. "
        "Use the calculator tool for any math. "
        "Use the search_docs tool to look up information in the documentation. "
        "If you do not know the answer, say so clearly. "
        "Do not invent facts."
    )
    agent = create_react_agent(llm, tools, prompt=system)
    return agent
