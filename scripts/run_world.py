"""
Build the IrishLogix simulation world from the CSO data.

Outputs (data/world/):
  port_days.csv         daily truth for Dublin and Rosslare (2017 to mid-2026)
  customs_history.csv   post-Brexit consignment records used to train and test C2
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd

from irishlogix.world.customs_world import customs_history
from irishlogix.world.port_world import simulate_port_days


def main():
    out = Path("data/world")
    out.mkdir(parents=True, exist_ok=True)
    activity = pd.read_csv("data/processed/cso_port_activity_matrix.csv")
    port_days = simulate_port_days(activity)
    port_days.to_csv(out / "port_days.csv", index=False)
    history = customs_history(port_days)
    history.to_csv(out / "customs_history.csv", index=False)
    print(f"port_days: {len(port_days)} rows | customs_history: {len(history)} rows")
    gb = history[history["origin_gb"]]
    print(f"GB consignments: {len(gb)}, mean clearance {gb['clearance_hours'].mean():.2f} h, "
          f"physical check rate {gb['physical_check'].mean():.3f}")


if __name__ == "__main__":
    main()
