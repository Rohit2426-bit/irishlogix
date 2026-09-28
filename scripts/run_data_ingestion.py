"""
Execution Script: Ingest and Process Official Irish CSO Maritime & Port Traffic Data.
Week 1 Deliverable for IrishLogix Research Practicum.
"""

import sys
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
from irishlogix.data.cso_loader import CSODataLoader

def main():
    print("=" * 70)
    print("IrishLogix Data Pipeline: Ingesting CSO Maritime Data (Week 1)")
    print("Student: Rohitkumar Amritlal Jaiswal (25119613) | NCI MSc Data Analytics")
    print("=" * 70)

    loader = CSODataLoader()

    print("\n[1/4] Ingesting TBQ01: Vessel Arrivals by Port...")
    arrivals_df = loader.get_port_arrivals()
    print(f"      Retrieved {len(arrivals_df)} arrival records.")
    print("      Ports available:", arrivals_df['port'].dropna().unique().tolist() if 'port' in arrivals_df.columns else "N/A")

    print("\n[2/4] Ingesting TBQ04: Ro-Ro Freight Units...")
    roro_df = loader.get_roro_freight_units()
    print(f"      Retrieved {len(roro_df)} Ro-Ro freight unit records.")

    print("\n[3/4] Ingesting TBQ05: Trade Region Goods Handled (GB & EU)...")
    trade_df = loader.get_trade_region_tonnage()
    print(f"      Retrieved {len(trade_df)} trade region tonnage records.")

    print("\n[4/4] Building Unified Port Activity Matrix (Dublin, Cork, Rosslare)...")
    activity_matrix = loader.build_port_activity_matrix()
    print(f"      Constructed matrix with {len(activity_matrix)} quarterly port observations.")

    # Save processed outputs
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)

    activity_matrix.to_csv(out_dir / "cso_port_activity_matrix.csv", index=False)
    arrivals_df.to_csv(out_dir / "cso_vessel_arrivals_cleaned.csv", index=False)
    roro_df.to_csv(out_dir / "cso_roro_traffic_cleaned.csv", index=False)
    trade_df.to_csv(out_dir / "cso_trade_region_tonnage_cleaned.csv", index=False)

    print("\n" + "=" * 70)
    print("SAMPLE CONGESTION FEATURE MATRIX (Most Recent Observations):")
    print("=" * 70)
    print(activity_matrix.tail(12).to_string(index=False))
    print("\n[SUCCESS] Processed datasets saved to data/processed/")

if __name__ == "__main__":
    main()
