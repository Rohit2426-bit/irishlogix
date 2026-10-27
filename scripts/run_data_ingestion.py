"""
Ingest and process the official CSO port traffic tables used by IrishLogix.

Outputs (data/processed/):
  cso_vessel_arrivals.csv      TBQ01 vessel arrivals (count)
  cso_roro_units.csv           TBQ03 loaded and empty Ro-Ro freight units
  cso_lolo_container_units.csv TBQ04 Lo-Lo container units (not Ro-Ro)
  cso_trade_region.csv         TBQ05 (2017 to 2019) + TBQ07 (2020 onwards) goods by region of trade
  cso_port_activity_matrix.csv Quarterly matrix for Dublin, Rosslare and Cork
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from irishlogix.data.cso_loader import CSODataLoader


def main():
    loader = CSODataLoader()
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "cso_vessel_arrivals.csv": loader.get_port_arrivals(),
        "cso_roro_units.csv": loader.get_roro_units(),
        "cso_lolo_container_units.csv": loader.get_lolo_container_units(),
        "cso_trade_region.csv": loader.get_trade_region_tonnage(),
        "cso_port_activity_matrix.csv": loader.build_port_activity_matrix(),
    }
    for name, df in outputs.items():
        df.to_csv(out_dir / name, index=False)
        print(f"{name:32s} {len(df):5d} rows")

    m = outputs["cso_port_activity_matrix.csv"]
    print("\nLatest quarters:")
    print(m[m["year"] >= 2025].to_string(index=False))


if __name__ == "__main__":
    main()
