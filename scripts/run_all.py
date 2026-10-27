"""
Rebuild every result from the raw CSO tables, in order, and record how long each step takes.

Usage (from the project root):  python scripts/run_all.py
Output: results/pipeline_timings.csv
"""

import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

STEPS = [
    ("CSO data ingestion", ["scripts/run_data_ingestion.py"]),
    ("Simulation world", ["scripts/run_world.py"]),
    ("C1 port congestion model", ["scripts/run_c1.py"]),
    ("C2 customs clearance model", ["scripts/run_c2.py"]),
    ("Planner benchmark (100 days)", ["scripts/run_benchmark.py"]),
    ("Scenarios (tight fleet, carbon price)", ["scripts/run_scenarios.py"]),
    ("Optimiser study", ["scripts/run_optimiser_study.py"]),
    ("Figures", ["scripts/make_figures.py"]),
    ("Unit tests", ["-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"]),
]


def main():
    rows = []
    for name, args in STEPS:
        t0 = time.time()
        done = subprocess.run([sys.executable, *args], capture_output=True, text=True)
        secs = time.time() - t0
        status = "ok" if done.returncode == 0 else "FAILED"
        rows.append({"step": name, "command": "python " + " ".join(args), "seconds": round(secs, 1), "status": status})
        print(f"{status:6s} {secs:7.1f}s  {name}", flush=True)
        if status != "ok":
            print(done.stdout[-2000:], done.stderr[-2000:])
            break
    Path("results").mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv("results/pipeline_timings.csv", index=False)


if __name__ == "__main__":
    main()
