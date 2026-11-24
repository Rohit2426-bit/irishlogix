"""
Week 1: run the FIFO baseline on 50 test loads and save the results.

Output (data/processed/): baseline_benchmark_results.csv and baseline_kpi_summary.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from irishlogix.simulation.baseline_dispatcher import BaselineFIFODispatcher


def main():
    dispatcher = BaselineFIFODispatcher(random_seed=42)
    demand_df = dispatcher.generate_benchmark_demand(num_consignments=50, gb_trade_ratio=0.55)
    print(f"{len(demand_df)} test loads\n")
    print(demand_df["origin_region"].value_counts().to_string(), "\n")
    print(demand_df["origin_port"].value_counts().to_string(), "\n")

    results_df, kpis = dispatcher.run_simulation(demand_df, diesel_price=1.75, ets2_price=80.0)

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out_dir / "baseline_benchmark_results.csv", index=False)
    with open(out_dir / "baseline_kpi_summary.json", "w") as f:
        json.dump(kpis, f, indent=2)

    print("Summary (costs in EUR, CO2 in kg):")
    for key, value in kpis.items():
        print(f"  {key:34s} {value}")

    cols = ["consignment_id", "origin_port", "destination_hub", "distance_km", "driving_hours",
            "total_idle_hours", "carbon_emissions_kg", "total_trip_cost_eur"]
    print("\nFirst 5 loads:")
    print(results_df[cols].head().to_string(index=False))
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
