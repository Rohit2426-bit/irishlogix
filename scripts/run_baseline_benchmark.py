"""
Execution Script: Run Baseline FIFO Dispatcher Simulation Benchmark.
Week 1 Deliverable for IrishLogix Research Practicum.
Demonstrates traditional un-optimized freight planning across Irish corridors.
"""

import sys
import json
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pandas as pd
from irishlogix.simulation.baseline_dispatcher import BaselineFIFODispatcher
from irishlogix.network.corridor_network import IrishFreightCorridorNetwork

def main():
    print("=" * 75)
    print("IrishLogix Baseline Simulation: Traditional FIFO Dispatcher Benchmark")
    print("Student: Rohitkumar Amritlal Jaiswal (25119613) | NCI MSc Data Analytics")
    print("=" * 75)

    dispatcher = BaselineFIFODispatcher(random_seed=42)

    print("\n[1/3] Generating Representative Benchmark Consignment Dataset (N=50)...")
    demand_df = dispatcher.generate_benchmark_demand(num_consignments=50, gb_trade_ratio=0.55)
    print(f"      Synthesized {len(demand_df)} cross-border freight movements.")
    print("      Trade Origins:")
    print(demand_df['origin_region'].value_counts().to_string())
    print("\n      Port Distribution:")
    print(demand_df['origin_port'].value_counts().to_string())

    print("\n[2/3] Simulating Baseline FIFO Operations (Unbuffered Port + Customs Delays)...")
    results_df, kpis = dispatcher.run_simulation(demand_df, diesel_price=1.75, ets2_price=80.0)

    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(out_dir / "baseline_benchmark_results.csv", index=False)

    with open(out_dir / "baseline_kpi_summary.json", "w") as f:
        json.dump(kpis, f, indent=2)

    print("\n[3/3] Baseline Simulation Complete! Benchmark KPIs:")
    print("-" * 75)
    print(f"  • Total Consignments Simulated:        {kpis['total_consignments']}")
    print(f"  • Total Road Transit Distance:         {kpis['total_distance_km']:,} km")
    print(f"  • Total Active Driving Time:           {kpis['total_driving_hours']} hours")
    print(f"  • Total Idle Waiting Time (Port/Gate): {kpis['total_idle_waiting_hours']} hours")
    print(f"  • Avg Idle Waiting Time per Consignment: {kpis['avg_idle_waiting_hours_per_trip']} hours")
    print(f"  • Total Diesel Fuel Consumed:          {kpis['total_fuel_consumed_litres']:,} Litres")
    print(f"  • Total Carbon Emissions (Tailpipe):   {kpis['total_carbon_emissions_kg']:,} kg CO2e")
    print(f"  • Average Carbon Intensity:            {kpis['avg_carbon_intensity_g_per_km']} g CO2e / km")
    print(f"  • Total Transport Operational Cost:    €{kpis['total_transport_cost_eur']:,}")
    print(f"  • Average Cost per Consignment:        €{kpis['avg_cost_per_trip_eur']:,}")
    print(f"  • Trips Requiring Mandatory Rest:      {kpis['trips_requiring_mandatory_rest']} / 50")
    print(f"  • Trips Exceeding EC 561 Daily Limit:  {kpis['trips_exceeding_daily_limit']} / 50")
    print("-" * 75)

    print("\nSample Consignment Dispatches (First 5 Rows):")
    cols_to_show = [
        "consignment_id", "origin_port", "destination_hub",
        "distance_km", "driving_hours", "total_idle_hours",
        "carbon_emissions_kg", "total_trip_cost_eur"
    ]
    print(results_df[cols_to_show].head().to_string(index=False))
    print(f"\n[SUCCESS] Baseline results saved to {out_dir / 'baseline_benchmark_results.csv'}")

if __name__ == "__main__":
    main()
