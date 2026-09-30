from __future__ import annotations
import time
from harness.schema import Case, RunResult, load_cases
from harness.agent import build_agent
from harness.tracing import TraceCollector
from harness.scorers import score_all, passed
from harness import store


def run_case(agent, case: Case, run_id: str) -> RunResult:
    tc = TraceCollector()
    start = time.time()
    try:
        out = agent.invoke(
            {"messages": [("user", case.input)]},
            config={"callbacks": [tc], "recursion_limit": 12},
        )
        messages = out.get("messages", [])
        answer = ""
        tool_calls = []
        for m in messages:
            if getattr(m, "type", "") == "ai" and m.content:
                answer = m.content
            for c in (getattr(m, "tool_calls", None) or []):
                tool_calls.append({"name": c["name"], "args": c.get("args", {})})

        return RunResult(
            answer=answer,
            tool_calls=tool_calls,
            latency_s=time.time() - start,
            input_tokens=tc.input_tokens,
            output_tokens=tc.output_tokens,
            events=tc.events,
        )
    except Exception as e:
        return RunResult(
            error=str(e),
            latency_s=time.time() - start,
            input_tokens=tc.input_tokens,
            output_tokens=tc.output_tokens,
        )


def run_suite(suite_path: str, label: str, model: str | None = None, repeats: int = 1):
    cases = load_cases(suite_path)
    agent = build_agent(model)
    run_id = store.new_run(label, model or "default", {"suite": suite_path, "repeats": repeats})

    print(f"Run {run_id}  label={label}  cases={len(cases)}  repeats={repeats}")
    for case in cases:
        for attempt in range(repeats):
            res = run_case(agent, case, run_id)
            scores = score_all(case, res)
            ok = passed(scores)
            store.save_result(run_id, case, attempt, res, scores, ok)
            status = "PASS" if ok else "FAIL"
            print(f"{status}  {case.id:<30} #{attempt}  {res.latency_s:>5.1f}s  tools={res.tool_names}")
    return run_id
