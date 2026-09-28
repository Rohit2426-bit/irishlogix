"""
Baseline FIFO Spreadsheet Dispatcher Simulation Engine.

Simulates traditional SME freight haulage operations across Irish corridors:
- Fixed deterministic scheduling (trucks dispatched to vessel docking time)
- Zero upstream predictive congestion buffering (causing terminal gate idling)
- Static shortest-distance routing
- Standard unbuffered customs inspection waits on post-Brexit UK trade lanes

This establishes the formal empirical baseline against which the coupled
IrishLogix ML + Pareto optimization engine will be benchmarked.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from ..network.corridor_network import IrishFreightCorridorNetwork
from ..utils.metrics import calculate_trip_metrics
from ..utils.config import VehicleParameters, RegulationEC561Rules


class BaselineFIFODispatcher:
    """Simulates traditional static First-In-First-Out (FIFO) spreadsheet freight dispatch."""

    def __init__(
        self,
        network: Optional[IrishFreightCorridorNetwork] = None,
        vehicle_params: Optional[VehicleParameters] = None,
        rules: Optional[RegulationEC561Rules] = None,
        random_seed: int = 42
    ):
        self.network = network or IrishFreightCorridorNetwork()
        self.vehicle_params = vehicle_params or VehicleParameters()
        self.rules = rules or RegulationEC561Rules()
        self.rng = np.random.default_rng(random_seed)

    def generate_benchmark_demand(
        self,
        num_consignments: int = 50,
        gb_trade_ratio: float = 0.55
    ) -> pd.DataFrame:
        """
        Synthesizes a realistic test benchmark dataset of cross-border Ro-Ro freight
        shipments landing at Irish ports, calibrated to CSO freight distributions.

        Args:
            num_consignments: Number of test freight loads to simulate.
            gb_trade_ratio: Proportion originating from Great Britain (subject to customs friction).

        Returns:
            DataFrame of consignment demand instances.
        """
        # Port probabilities based on CSO Ro-Ro shares (Dublin ~70%, Rosslare ~20%, Cork ~10%)
        ports = ["PORT_DUBLIN", "PORT_ROSSLARE", "PORT_CORK"]
        port_probs = [0.70, 0.20, 0.10]

        # Inland destinations
        destinations = [
            "HUB_DUBLIN_M50", "HUB_ATHLONE", "HUB_LIMERICK",
            "HUB_GALWAY", "HUB_WATERFORD_INLAND", "HUB_DUNDALK"
        ]

        commodities = ["General Merchandise", "Agrifood / SPS Sensitive", "Machinery & Parts"]
        commodity_probs = [0.55, 0.30, 0.15]

        consignments = []
        for i in range(1, num_consignments + 1):
            origin_port = self.rng.choice(ports, p=port_probs)

            # Pick destination different from origin port county
            valid_dests = [d for d in destinations if d != origin_port]
            dest = self.rng.choice(valid_dests)

            is_gb_origin = bool(self.rng.random() < gb_trade_ratio)
            commodity = self.rng.choice(commodities, p=commodity_probs)

            # Scheduled arrival hour of ferry (0 to 23 hours in the day)
            vessel_arrival_hour = round(float(self.rng.uniform(4.0, 22.0)), 2)

            consignments.append({
                "consignment_id": f"CSG-{i:04d}",
                "origin_port": origin_port,
                "destination_hub": dest,
                "is_gb_origin": is_gb_origin,
                "origin_region": "Great Britain (Post-Brexit)" if is_gb_origin else "EU Internal Market",
                "commodity": commodity,
                "vessel_arrival_hour": vessel_arrival_hour,
            })

        return pd.DataFrame(consignments)

    def simulate_trip(
        self,
        consignment: Dict[str, Any],
        diesel_price: float = 1.75,
        ets2_price: float = 80.0
    ) -> Dict[str, Any]:
        """
        Simulates one consignment transit under baseline FIFO dispatch rules.
        """
        origin = consignment["origin_port"]
        destination = consignment["destination_hub"]
        is_gb = consignment["is_gb_origin"]
        commodity = consignment["commodity"]

        # 1. Routing: Static shortest road distance via NetworkX
        route_info = self.network.get_shortest_route(origin, destination, weight="distance_km")
        distance_km = route_info["total_distance_km"]
        driving_hours = route_info["total_driving_hours"]
        toll_eur = route_info["total_toll_eur"]

        # 2. Port Gate Congestion Waiting (Unbuffered)
        # Without predictive scheduling, trucks arriving at peak vessel discharge face gate queues.
        # Calibrated baseline distribution: Log-normal waiting time (mean ~0.8h at Dublin, 0.4h at Rosslare/Cork)
        if origin == "PORT_DUBLIN":
            gate_wait_hours = float(self.rng.lognormal(mean=-0.2, sigma=0.5))  # median ~0.8h
        else:
            gate_wait_hours = float(self.rng.lognormal(mean=-0.9, sigma=0.4))  # median ~0.4h
        gate_wait_hours = max(0.1, min(gate_wait_hours, 3.5))

        # 3. Post-Brexit Customs Delay
        # EU internal market consignments clear directly (green channel ~ 0.1h documentary check)
        # GB consignments face potential physical/documentary hold:
        # Agrifood/SPS faces higher inspection probability and duration
        customs_wait_hours = 0.05
        if is_gb:
            if commodity == "Agrifood / SPS Sensitive":
                # 35% random physical SPS inspection rate
                if self.rng.random() < 0.35:
                    customs_wait_hours = float(self.rng.uniform(1.8, 5.0))
                else:
                    customs_wait_hours = float(self.rng.uniform(0.4, 1.2))
            else:
                # 15% random documentary/customs hold rate
                if self.rng.random() < 0.15:
                    customs_wait_hours = float(self.rng.uniform(1.0, 3.0))
                else:
                    customs_wait_hours = float(self.rng.uniform(0.2, 0.8))

        total_idle_waiting_hours = gate_wait_hours + customs_wait_hours

        # 4. Compute comprehensive operational metrics
        trip_metrics = calculate_trip_metrics(
            distance_km=distance_km,
            driving_hours=driving_hours,
            idle_waiting_hours=total_idle_waiting_hours,
            diesel_price_eur_per_litre=diesel_price,
            ets2_price_eur_per_tonne=ets2_price,
            vehicle=self.vehicle_params,
            rules=self.rules
        )

        # Add tolls to total operational cost
        total_trip_cost = trip_metrics["total_operational_cost_eur"] + toll_eur

        result = {
            "consignment_id": consignment["consignment_id"],
            "origin_port": origin,
            "destination_hub": destination,
            "origin_region": consignment["origin_region"],
            "commodity": commodity,
            "distance_km": distance_km,
            "driving_hours": driving_hours,
            "gate_wait_hours": round(gate_wait_hours, 2),
            "customs_wait_hours": round(customs_wait_hours, 2),
            "total_idle_hours": round(total_idle_waiting_hours, 2),
            "rest_break_hours": trip_metrics["rest_break_hours"],
            "total_transit_elapsed_hours": round(trip_metrics["total_trip_elapsed_hours"], 2),
            "fuel_consumed_litres": trip_metrics["total_fuel_litres"],
            "carbon_emissions_kg": trip_metrics["total_carbon_emissions_kg"],
            "carbon_intensity_g_per_km": trip_metrics["carbon_intensity_g_per_km"],
            "driver_cost_eur": trip_metrics["driver_wage_cost_eur"],
            "fuel_cost_eur": trip_metrics["fuel_cost_eur"],
            "toll_cost_eur": round(toll_eur, 2),
            "ets2_tax_eur": trip_metrics["ets2_carbon_cost_eur"],
            "total_trip_cost_eur": round(total_trip_cost, 2),
            "ec561_break_required": trip_metrics["ec561_break_required"],
            "ec561_limit_exceeded": trip_metrics["ec561_daily_limit_exceeded"],
        }
        return result

    def run_simulation(
        self,
        demand_df: pd.DataFrame,
        diesel_price: float = 1.75,
        ets2_price: float = 80.0
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Executes baseline simulation across a full demand dataset.

        Returns:
            Tuple of (detailed trip records DataFrame, aggregate benchmark KPI summary dict).
        """
        records = []
        for _, row in demand_df.iterrows():
            record = self.simulate_trip(
                row.to_dict(),
                diesel_price=diesel_price,
                ets2_price=ets2_price
            )
            records.append(record)

        df_results = pd.DataFrame(records)

        kpis = {
            "total_consignments": len(df_results),
            "total_distance_km": round(df_results["distance_km"].sum(), 1),
            "total_driving_hours": round(df_results["driving_hours"].sum(), 1),
            "total_idle_waiting_hours": round(df_results["total_idle_hours"].sum(), 1),
            "avg_idle_waiting_hours_per_trip": round(df_results["total_idle_hours"].mean(), 2),
            "total_fuel_consumed_litres": round(df_results["fuel_consumed_litres"].sum(), 1),
            "total_carbon_emissions_kg": round(df_results["carbon_emissions_kg"].sum(), 1),
            "avg_carbon_intensity_g_per_km": round(df_results["carbon_intensity_g_per_km"].mean(), 1),
            "total_transport_cost_eur": round(df_results["total_trip_cost_eur"].sum(), 2),
            "avg_cost_per_trip_eur": round(df_results["total_trip_cost_eur"].mean(), 2),
            "trips_requiring_mandatory_rest": int(df_results["ec561_break_required"].sum()),
            "trips_exceeding_daily_limit": int(df_results["ec561_limit_exceeded"].sum()),
        }

        return df_results, kpis
