# Agent Eval Harness

Open-source evaluation harness for tool-using LLM agents (LangGraph).

Measure whether a change makes the agent better or worse on a fixed golden set — with pass/fail, tool checks, and a React dashboard.

## Features (Week 1)

- ReAct agent with calculator + document search tools
- YAML golden cases (math, RAG, unanswerable, multi-step)
- Deterministic scorers (contains, safety, tools, efficiency)
- Postgres storage (runs + results)
- CLI: run, compare
- React + FastAPI dashboard

## Quickstart

1. Python env

python3 -m venv .venv && source .venv/bin/activate
pip install langgraph langchain-core langchain-openai langchain-community pydantic pyyaml python-dotenv pandas "psycopg[binary]" fastapi uvicorn

2. Postgres (Docker)

docker run -d --name evalpg -e POSTGRES_PASSWORD=eval -e POSTGRES_DB=eval -p 5433:5432 postgres:16

3. Config

cp .env.example .env
Set LLM_BASE_URL, LLM_API_KEY, AGENT_MODEL, DATABASE_URL in .env

4. Run eval

python -m harness.cli run --suite cases/basic.yaml --label my-run
python -m harness.cli compare my-run other-run

5. Dashboard

Terminal A: uvicorn dashboard.backend.main:app --reload --port 8000
Terminal B: cd dashboard/frontend && npm install && npm run dev
Open http://localhost:5173

## Project layout

harness/     - agent, tools, scorers, store, runner, cli
cases/       - golden YAML suites
corpus/      - documents for search_docs
dashboard/   - FastAPI + React UI
docs/        - design.md, learnings.md

## What pass means

A case passes when active scorers all score at least 0.75 (keyword checks, tool use, efficiency). See docs/design.md.

## Free models

Works with OpenRouter free models. They can be rate-limited (429/503); re-run or use a more stable endpoint for reliable numbers.

## Roadmap

Follows a 10-week plan: real vector retrieval (Qdrant), richer scorers, judge calibration, CI regression gates, adversarial suite, experiments.

## License

MIT (intended). Add a LICENSE file when you publish.

