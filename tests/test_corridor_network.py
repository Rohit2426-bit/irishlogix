"""
Unit tests for Irish freight corridor network graph.
"""

import pytest
import networkx as nx
import pandas as pd
from irishlogix.network.corridor_network import IrishFreightCorridorNetwork, NODES, EDGES

@pytest.fixture
def network():
    return IrishFreightCorridorNetwork()

def test_graph_initialization(network):
    assert len(network.graph.nodes) == len(NODES)
    assert len(network.graph.edges) == len(EDGES)
    assert nx.is_connected(network.graph)

def test_shortest_route_dublin_to_galway(network):
    route = network.get_shortest_route("PORT_DUBLIN", "HUB_GALWAY", weight="distance_km")
    assert route["origin"] == "PORT_DUBLIN"
    assert route["destination"] == "HUB_GALWAY"
    assert route["total_distance_km"] > 200.0
    assert route["total_driving_hours"] > 2.0
    assert "HUB_ATHLONE" in route["path_nodes"]

def test_distance_matrix_dimensions(network):
    matrix = network.compute_distance_matrix()
    assert isinstance(matrix, pd.DataFrame)
    assert matrix.shape == (len(NODES), len(NODES))
    assert matrix.loc["PORT_DUBLIN", "PORT_DUBLIN"] == 0.0
