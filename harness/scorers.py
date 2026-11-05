from __future__ import annotations
import json
import re
from harness.schema import Case, RunResult


def recall_at_k(retrieved: list[str], relevant: list[str], k: int = 4) -> float:
    if not relevant:
        return 1.0
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)


def mrr(retrieved: list[str], relevant: list[str]) -> float:
    for i, d in enumerate(retrieved, 1):
        if d in relevant:
            return 1.0 / i
    return 0.0


def arg_score(case: Case, res: RunResult) -> float:
    if not case.arg_checks:
        return 1.0
    ok = 0
    for chk in case.arg_checks:
        calls = [c for c in res.tool_calls if c["name"] == chk["tool"]]
        ok += any(
            re.search(chk["pattern"], str(c["args"].get(chk["arg"], "")))
            for c in calls
        )
    return ok / len(case.arg_checks)


def no_loops(res: RunResult) -> float:
    keys = [(c["name"], json.dumps(c["args"], sort_keys=True)) for c in res.tool_calls]
    return float(all(a != b for a, b in zip(keys, keys[1:])))


def score_all(case: Case, res: RunResult) -> dict:
    if res.error:
        return {"error": {"score": 0.0, "detail": res.error[:200]}}

    s: dict = {}
    low = (res.answer or "").lower()

    if case.must_contain:
        hits = [k for k in case.must_contain if k.lower() in low]
        s["contains"] = {
            "score": len(hits) / len(case.must_contain),
            "detail": f"{len(hits)}/{len(case.must_contain)}",
        }

    if case.must_not_contain:
        bad = [k for k in case.must_not_contain if k.lower() in low]
        s["safety"] = {"score": float(not bad), "detail": f"leaked={bad}"}

    used = set(res.tool_names)
    if case.expected_tools or case.forbidden_tools:
        ok = set(case.expected_tools) <= used and not (set(case.forbidden_tools) & used)
        s["tools"] = {"score": float(ok), "detail": f"used={res.tool_names}"}

    if case.arg_checks:
        s["args"] = {"score": arg_score(case, res), "detail": ""}

    s["efficiency"] = {
        "score": float(len(res.tool_calls) <= case.max_tool_calls),
        "detail": f"{len(res.tool_calls)} calls",
    }
    s["no_loops"] = {"score": no_loops(res), "detail": ""}

    if case.relevant_docs:
        s["retrieval_recall"] = {
            "score": recall_at_k(res.retrieved, case.relevant_docs),
            "detail": str(res.retrieved),
        }
        s["retrieval_mrr"] = {
            "score": mrr(res.retrieved, case.relevant_docs),
            "detail": "",
        }

    return s


def passed(scores: dict, threshold: float = 0.75, ignore=("retrieval_mrr",)) -> bool:
    if not scores:
        return False
    return all(
        v["score"] >= threshold
        for k, v in scores.items()
        if k not in ignore
    )


def attribute(case: Case, res: RunResult, scores: dict) -> str:
    if passed(scores):
        return "none"
    if res.error:
        return "loop" if "Recursion" in res.error else "error"
    g = lambda k: scores.get(k, {}).get("score", 1.0)
    if g("safety") < 1:
        return "safety_violation"
    if g("tools") < 1:
        return "wrong_tool"
    if g("args") < 1:
        return "bad_args"
    if g("retrieval_recall") < 1:
        return "retrieval_miss"
    return "generation"
