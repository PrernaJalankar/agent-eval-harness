from __future__ import annotations
import json
import os
import uuid
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


def conn():
    c = psycopg.connect(
        os.environ["DATABASE_URL"],
        row_factory=dict_row,
        autocommit=True,
    )
    c.execute("""
        CREATE TABLE IF NOT EXISTS runs(
            id text PRIMARY KEY,
            label text,
            model text,
            git_sha text,
            config jsonb,
            judge_version text,
            created timestamptz DEFAULT now()
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS results(
            id serial PRIMARY KEY,
            run_id text REFERENCES runs(id),
            case_id text,
            attempt int DEFAULT 0,
            answer text,
            tool_calls jsonb,
            retrieved jsonb,
            contexts jsonb,
            latency real,
            in_tok int,
            out_tok int,
            cost_usd real DEFAULT 0,
            scores jsonb,
            passed boolean,
            failure_type text
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS labels(
            result_id int PRIMARY KEY REFERENCES results(id),
            human_score int,
            note text,
            labeled_at timestamptz DEFAULT now()
        )
    """)
    return c


def _sha() -> str:
    try:
        import subprocess
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def new_run(label: str, model: str, config: dict | None = None) -> str:
    rid = uuid.uuid4().hex[:8]
    with conn() as c:
        c.execute(
            """INSERT INTO runs(id, label, model, git_sha, config, judge_version)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                rid,
                label,
                model,
                _sha(),
                json.dumps(config or {}),
                os.getenv("JUDGE_VERSION", "v1"),
            ),
        )
    return rid


def save_result(run_id, case, attempt, res, scores, ok, failure_type="none", cost=0.0):
    with conn() as c:
        c.execute(
            """INSERT INTO results(
                run_id, case_id, attempt, answer, tool_calls, retrieved, contexts,
                latency, in_tok, out_tok, cost_usd, scores, passed, failure_type
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                run_id,
                case.id,
                attempt,
                res.answer,
                json.dumps(res.tool_calls),
                json.dumps(getattr(res, "retrieved", [])),
                json.dumps(getattr(res, "contexts", [])),
                res.latency_s,
                res.input_tokens,
                res.output_tokens,
                cost,
                json.dumps(scores),
                ok,
                failure_type,
            ),
        )


def latest_run_id(label: str) -> str:
    with conn() as c:
        row = c.execute(
            "SELECT id FROM runs WHERE label=%s ORDER BY created DESC LIMIT 1",
            (label,),
        ).fetchone()
    if not row:
        raise SystemExit(f"no run with label '{label}'")
    return row["id"]


def results(run_id: str) -> list[dict]:
    with conn() as c:
        return c.execute(
            "SELECT * FROM results WHERE run_id=%s", (run_id,)
        ).fetchall()
