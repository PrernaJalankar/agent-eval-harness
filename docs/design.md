# Agent Eval Harness — Design

## What questions does this harness answer?

1. Did this change make the agent better or worse?
2. On which kinds of tasks (math, docs, unanswerable, multi-step)?
3. Did the agent use the right tools?
4. Did it stay safe (no forbidden content / no invented facts)?

## Who runs it?

- Developers, before merging a change (smoke suite)
- Nightly / full suite for deeper checks
- Anyone comparing two prompts, models, or tool setups

## What does "pass" mean?

A case passes when all active scorers score at least 0.75:

- contains — required phrases appear in the answer
- safety — forbidden phrases do not appear
- tools — expected tools were used; forbidden tools were not
- efficiency — tool-call count is within the limit

Later weeks add retrieval metrics, faithfulness, and an LLM judge.

## Principles

- Public data only
- Repeatable runs stored in Postgres with label and git SHA
- Comparable via the compare command
- Cheap smoke path for PRs; fuller suite for deeper evaluation

## Current stack (Week 1)

- Agent: LangGraph ReAct + OpenRouter-compatible LLM
- Tools: calculator, keyword search over corpus/
- Store: Postgres
- CLI: run, compare
- Dashboard: React + FastAPI
