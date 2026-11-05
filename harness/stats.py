from __future__ import annotations
import math
import random
from collections import defaultdict


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def per_case_rates(rows: list[dict]) -> dict[str, float]:
    d: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        d[r["case_id"]].append(1.0 if r["passed"] else 0.0)
    return {k: sum(v) / len(v) for k, v in d.items()}


def paired_bootstrap(
    a: dict[str, float],
    b: dict[str, float],
    n: int = 5000,
    seed: int = 0,
) -> tuple[float, float, float]:
    """Mean per-case pass-rate difference (b - a) with 95% bootstrap CI."""
    ids = sorted(set(a) & set(b))
    if not ids:
        return 0.0, 0.0, 0.0
    diffs = [b[i] - a[i] for i in ids]
    rng = random.Random(seed)
    means = sorted(
        sum(rng.choices(diffs, k=len(diffs))) / len(diffs) for _ in range(n)
    )
    return (
        sum(diffs) / len(diffs),
        means[int(0.025 * n)],
        means[int(0.975 * n)],
    )


def consistency(rows: list[dict]) -> float:
    """Share of cases whose attempts all agree (all pass or all fail)."""
    d: dict[str, set] = defaultdict(set)
    for r in rows:
        d[r["case_id"]].add(bool(r["passed"]))
    if not d:
        return 0.0
    return sum(len(v) == 1 for v in d.values()) / len(d)
