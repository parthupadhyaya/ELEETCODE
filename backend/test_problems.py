"""Runs every problem through the tracer and checks its result.

Usage: venv\Scripts\python test_problems.py
"""

import sys

from problems import PROBLEMS
from tracer import run

failures = 0
for p in PROBLEMS:
    out = run(p["code"], p["run"])
    steps = len(out["steps"])
    problem = f'{p["num"]:>4} {p["title"]}'
    if out["error"]:
        print(f"FAIL {problem}: {out['error']}")
        failures += 1
    elif out["truncated"]:
        print(f"FAIL {problem}: hit the step limit ({steps} steps)")
        failures += 1
    elif p["expect"] is not None and out.get("result") != p["expect"]:
        print(f"FAIL {problem}: got {out.get('result')}, expected {p['expect']}")
        failures += 1
    elif steps == 0:
        print(f"FAIL {problem}: no steps recorded")
        failures += 1
    elif steps > 900:
        print(f"WARN {problem}: {steps} steps (slow to step through)")

print(f"\n{len(PROBLEMS) - failures}/{len(PROBLEMS)} passed")
sys.exit(1 if failures else 0)
