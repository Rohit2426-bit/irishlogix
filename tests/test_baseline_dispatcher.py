"""
Unit tests for baseline FIFO dispatcher simulation.
"""

import pytest
import pandas as pd
from irishlogix.simulation.baseline_dispatcher import BaselineFIFODispatcher

@pytest.fixture
def dispatcher():
    return BaselineFIFODispatcher(random_seed=123)

def test_generate_demand(dispatcher):
    demand = dispatcher.generate_benchmark_demand(num_consignments=10)
    assert isinstance(demand, pd.DataFrame)
    assert len(demand) == 10
    assert "consignment_id" in demand.columns
    assert "origin_port" in demand.columns
    assert "destination_hub" in demand.columns

def test_simulate_trip(dispatcher):
    consignment = {
        "consignment_id": "TEST-001",
        "origin_port": "PORT_DUBLIN",
        "destination_hub": "HUB_LIMERICK",
        "is_gb_origin": True,
        "origin_region": "Great Britain (Post-Brexit)",
        "commodity": "Agrifood / SPS Sensitive",
        "vessel_arrival_hour": 10.5
    }
    result = dispatcher.simulate_trip(consignment)
    assert result["consignment_id"] == "TEST-001"
    assert result["distance_km"] > 0
    assert result["driving_hours"] > 0
    assert result["total_idle_hours"] > 0
    assert result["total_trip_cost_eur"] > 0
    assert result["carbon_emissions_kg"] > 0

def test_full_simulation_run(dispatcher):
    demand = dispatcher.generate_benchmark_demand(num_consignments=5)
    results_df, kpis = dispatcher.run_simulation(demand)
    assert len(results_df) == 5
    assert kpis["total_consignments"] == 5
    assert kpis["total_transport_cost_eur"] > 0
    assert kpis["total_carbon_emissions_kg"] > 0
