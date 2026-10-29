from __future__ import annotations
import argparse
from harness.runner import run_suite
from harness import store
from harness.ingest import ingest


def main():
    parser = argparse.ArgumentParser(prog="agent-eval")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run a suite of cases")
    p_run.add_argument("--suite", default="cases/basic.yaml")
    p_run.add_argument("--label", required=True)
    p_run.add_argument("--model", default=None)
    p_run.add_argument("--repeats", type=int, default=1)

    p_cmp = sub.add_parser("compare", help="Compare two labels")
    p_cmp.add_argument("a")
    p_cmp.add_argument("b")

    p_ing = sub.add_parser("ingest", help="Ingest corpus into Qdrant")
    p_ing.add_argument("--corpus", default="corpus")
    p_ing.add_argument("--size", type=int, default=800)
    p_ing.add_argument("--overlap", type=int, default=100)

    args = parser.parse_args()

    if args.cmd == "run":
        run_suite(args.suite, args.label, args.model, args.repeats)
    elif args.cmd == "compare":
        ra = store.results(store.latest_run_id(args.a))
        rb = store.results(store.latest_run_id(args.b))
        for name, rows in ((args.a, ra), (args.b, rb)):
            k = sum(1 for r in rows if r["passed"])
            n = len(rows)
            print(f"{name:<14} pass {k}/{n} = {k/n:.1%}" if n else f"{name:<14} no results")
        print("\nChanged cases:")
        pa = {r["case_id"]: r["passed"] for r in ra}
        pb = {r["case_id"]: r["passed"] for r in rb}
        for cid in sorted(set(pa) | set(pb)):
            if pa.get(cid) != pb.get(cid):
                print(f"  {cid}: {pa.get(cid)} → {pb.get(cid)}")
    elif args.cmd == "ingest":
        n = ingest(args.corpus, args.size, args.overlap)
        print(f"Ingested {n} chunks from {args.corpus}")


if __name__ == "__main__":
    main()
