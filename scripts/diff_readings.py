#!/usr/bin/env python3
"""Find inputs on which executable readings of a specification disagree.

Each reading is a Python file in one directory that defines:

    INPUTS = {"amount": [5000, 10000], "approved": [False, True], ...}
    def outcome(case: dict) -> str: ...

INPUTS lists the values that reading considers relevant for each input.
The script takes the union over all readings, adds the neighbours v-1 and v+1
of every integer value, enumerates the combinations (sampling past
--max-cases), runs every reading on every case, and reports each distinct
pattern of disagreement: which readings agree with which, and the shape of
their labels with numbers ignored, so `fee=950;blocked` and `fee=1000;blocked`
are one pattern. Patterns that split the readings into more groups come
first: their example is the most informative question to put to the spec
author. For each pattern it shows up to three examples that change different
inputs from the baseline (the first value listed for each input), smallest
first, because one pattern can have several causes.

This is bounded testing: it finds disagreements among the cases it checks and
cannot show that the readings agree anywhere else.

Usage: python3 scripts/diff_readings.py READINGS_DIR [--max-cases N] [--json]
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import random
import re
import sys
from pathlib import Path
from typing import Any, Callable


def load_readings(directory: Path) -> dict[str, tuple[dict[str, list[Any]], Callable[[dict], Any]]]:
    readings = {}
    for path in sorted(directory.glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"reading_{path.stem}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "outcome"):
            raise ValueError(f"{path.name} defines no outcome(case)")
        readings[path.stem] = (getattr(module, "INPUTS", {}), module.outcome)
    if len(readings) < 2:
        raise ValueError("need at least two readings")
    return readings


def candidate_values(readings) -> dict[str, list[Any]]:
    """Listed values first (the first one is the baseline), then integer neighbours.

    A non-negative value never gets a negative neighbour, so 0 does not produce -1.
    """
    values: dict[str, list[Any]] = {}
    for inputs, _ in readings.values():
        for name, listed in inputs.items():
            bucket = values.setdefault(name, [])
            bucket.extend(v for v in listed if v not in bucket)
    for bucket in values.values():
        for value in list(bucket):
            if type(value) is not int:
                continue
            for v in (value - 1, value + 1):
                if (v >= 0 or value < 0) and v not in bucket:
                    bucket.append(v)
    return values


def cases(values: dict[str, list[Any]], max_cases: int, seed: int = 0):
    names = list(values)
    total = 1
    for name in names:
        total *= len(values[name])
    if total <= max_cases:
        for combo in itertools.product(*(values[n] for n in names)):
            yield dict(zip(names, combo))
        return
    # Too many combinations: every single- and two-input change from the
    # baseline, then a random sample of the rest.
    baseline = {n: values[n][0] for n in names}
    seen = set()
    for k in (1, 2):
        for chosen in itertools.combinations(names, k):
            for combo in itertools.product(*(values[n] for n in chosen)):
                case = dict(baseline, **dict(zip(chosen, combo)))
                key = tuple(case[n] for n in names)
                if key not in seen:
                    seen.add(key)
                    yield case
    rng = random.Random(seed)
    while len(seen) < max_cases:
        case = {n: rng.choice(values[n]) for n in names}
        key = tuple(case[n] for n in names)
        if key not in seen:
            seen.add(key)
            yield case


def run(reading: Callable[[dict], Any], case: dict) -> str:
    try:
        return str(reading(dict(case)))
    except Exception as exc:  # a reading that cannot handle a case is itself a finding
        return f"ERROR: {type(exc).__name__}: {exc}"


def diff(readings, max_cases: int) -> dict[str, Any]:
    values = candidate_values(readings)
    baseline = {n: v[0] for n, v in values.items()}
    names = list(readings)
    patterns: dict[tuple, dict[str, Any]] = {}
    checked = 0
    for case in cases(values, max_cases):
        checked += 1
        outcomes = tuple(run(readings[n][1], case) for n in names)
        if len(set(outcomes)) == 1:
            continue
        moved = frozenset(k for k in case if case[k] != baseline[k])
        partition = tuple(outcomes.index(o) for o in outcomes)
        shapes = tuple(re.sub(r"\d+(\.\d+)?", "#", o) for o in outcomes)
        entry = patterns.setdefault((partition, shapes), {"count": 0, "by_inputs": {}})
        entry["count"] += 1
        # Keep one example per set of changed inputs; drop sets that contain a smaller kept set.
        if moved not in entry["by_inputs"] and not any(s < moved for s in entry["by_inputs"]):
            for s in [s for s in entry["by_inputs"] if moved < s]:
                del entry["by_inputs"][s]
            entry["by_inputs"][moved] = (case, outcomes)
    rows = []
    for (partition, _), v in patterns.items():
        examples = sorted(v["by_inputs"].items(), key=lambda kv: (len(kv[0]), sorted(kv[0])))[:3]
        rows.append({
            "outcomes": dict(zip(names, examples[0][1][1])),
            "groups": len(set(partition)),
            "largest_group": max(partition.count(g) for g in partition),
            "count": v["count"],
            "examples": [case for _, (case, _) in examples],
            "example_outcomes": [dict(zip(names, o)) for _, (_, o) in examples],
            "changed": len(examples[0][0]),
        })
    # Most informative first: more groups, then a smaller largest group, then fewer changed inputs.
    rows.sort(key=lambda r: (-r["groups"], r["largest_group"], r["changed"], -r["count"]))
    return {"readings": names, "inputs": values, "cases_checked": checked, "divergences": rows}


def render(result: dict[str, Any]) -> str:
    names = result["readings"]
    lines = [
        f"Checked {result['cases_checked']} cases over inputs: "
        + ", ".join(f"{k}={v}" for k, v in result["inputs"].items()),
        f"Distinct disagreement patterns: {len(result['divergences'])}",
    ]
    if result["divergences"]:
        lines += ["", "| # | Example cases (smallest first) | " + " | ".join(names) + " | Groups | Cases |",
                  "|---|---|" + "---|" * len(names) + "---|---|"]
        for i, row in enumerate(result["divergences"], 1):
            for j, (case, outcomes) in enumerate(zip(row["examples"], row["example_outcomes"])):
                text = ", ".join(f"{k}={v}" for k, v in case.items())
                cells = " | ".join(outcomes[n] for n in names)
                label, groups, count = (f"D{i}", str(row["groups"]), str(row["count"])) if j == 0 else ("", "", "")
                lines.append(f"| {label} | {text} | {cells} | {groups} | {count} |")
    if any(row["changed"] == 0 for row in result["divergences"]):
        lines += ["", "Note: the readings already disagree on the baseline case. If their labels mean "
                  "the same thing, make the labels identical and rerun."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("directory", type=Path)
    parser.add_argument("--max-cases", type=int, default=20000)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = diff(load_readings(args.directory), args.max_cases)
    print(json.dumps(result, indent=2, default=str) if args.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
