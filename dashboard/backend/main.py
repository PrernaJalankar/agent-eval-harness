from __future__ import annotations
import os
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

app = FastAPI(title="Agent Eval Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn():
    return psycopg.connect(
        os.environ["DATABASE_URL"],
        row_factory=dict_row,
        autocommit=True,
    )


@app.get("/api/runs")
def list_runs() -> list[dict[str, Any]]:
    with get_conn() as c:
        rows = c.execute("""
            SELECT r.id, r.label, r.model, r.created,
                   COUNT(res.id) AS total,
                   COUNT(res.id) FILTER (WHERE res.passed) AS passed
            FROM runs r
            LEFT JOIN results res ON res.run_id = r.id
            GROUP BY r.id
            ORDER BY r.created DESC
        """).fetchall()
    out = []
    for r in rows:
        total = r["total"] or 0
        passed = r["passed"] or 0
        out.append({
            "id": r["id"],
            "label": r["label"],
            "model": r["model"],
            "created": r["created"].isoformat() if r["created"] else None,
            "total": total,
            "passed": passed,
            "pass_rate": round(passed / total, 3) if total else 0.0,
        })
    return out


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    with get_conn() as c:
        run = c.execute(
            "SELECT id, label, model, created FROM runs WHERE id = %s",
            (run_id,),
        ).fetchone()
        if not run:
            raise HTTPException(404, "Run not found")
        results = c.execute(
            """SELECT case_id, attempt, answer, tool_calls, latency,
                      in_tok, out_tok, scores, passed, failure_type
               FROM results WHERE run_id = %s ORDER BY case_id, attempt""",
            (run_id,),
        ).fetchall()
    return {
        "id": run["id"],
        "label": run["label"],
        "model": run["model"],
        "created": run["created"].isoformat() if run["created"] else None,
        "results": [
            {
                "case_id": r["case_id"],
                "attempt": r["attempt"],
                "answer": r["answer"],
                "tool_calls": r["tool_calls"],
                "latency": r["latency"],
                "in_tok": r["in_tok"],
                "out_tok": r["out_tok"],
                "scores": r["scores"],
                "passed": r["passed"],
                "failure_type": r["failure_type"],
            }
            for r in results
        ],
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}
