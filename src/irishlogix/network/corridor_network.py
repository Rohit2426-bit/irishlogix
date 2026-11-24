"""
Road network for the study, built with NetworkX.

Nodes are the main ports (Dublin, Cork, Rosslare, Waterford) and the inland freight hubs.
Edges are the main truck roads between them, with distance, typical truck speed and tolls.
"""

import networkx as nx
import pandas as pd
from typing import Dict, List, Tuple, Any

# Nodes with latitude, longitude and type (port or hub)
NODES: Dict[str, Dict[str, Any]] = {
    "PORT_DUBLIN": {
        "name": "Dublin Port (Alexandra Quay / Ro-Ro)",
        "lat": 53.3498, "lon": -6.2085, "type": "port", "county": "Dublin"
    },
    "PORT_CORK": {
        "name": "Port of Cork (Ringaskiddy / Tivoli)",
        "lat": 51.8601, "lon": -8.3183, "type": "port", "county": "Cork"
    },
    "PORT_ROSSLARE": {
        "name": "Rosslare Europort (Stena / Irish Ferries)",
        "lat": 52.2530, "lon": -6.3377, "type": "port", "county": "Wexford"
    },
    "PORT_WATERFORD": {
        "name": "Port of Waterford (Belview)",
        "lat": 52.2600, "lon": -7.0600, "type": "port", "county": "Kilkenny"
    },
    "HUB_DUBLIN_M50": {
        "name": "Dublin M50 Logistics Hub (Ballymount/Red Cow)",
        "lat": 53.3150, "lon": -6.3600, "type": "hub", "county": "Dublin"
    },
    "HUB_ATHLONE": {
        "name": "Athlone Central Logistics Hub (Midlands M6)",
        "lat": 53.4239, "lon": -7.9407, "type": "hub", "county": "Westmeath"
    },
    "HUB_LIMERICK": {
        "name": "Limerick & Shannon Airport Freight Park (M7/M18)",
        "lat": 52.6680, "lon": -8.6300, "type": "hub", "county": "Limerick"
    },
    "HUB_GALWAY": {
        "name": "Galway East Industrial Logistics Park (M6)",
        "lat": 53.2707, "lon": -9.0568, "type": "hub", "county": "Galway"
    },
    "HUB_CORK_INLAND": {
        "name": "Cork Little Island Industrial Estate (N25)",
        "lat": 51.9050, "lon": -8.3650, "type": "hub", "county": "Cork"
    },
    "HUB_WATERFORD_INLAND": {
        "name": "Waterford Industrial Park (M9/N25)",
        "lat": 52.2593, "lon": -7.1101, "type": "hub", "county": "Waterford"
    },
    "HUB_DUNDALK": {
        "name": "Dundalk Northern Corridor Gateway (M1/A1)",
        "lat": 54.0039, "lon": -6.4022, "type": "hub", "county": "Louth"
    },
}

# Road links (both directions) with distance in km, truck speed in km/h, road type and toll
EDGES: List[Tuple[str, str, Dict[str, Any]]] = [
    # Dublin Port connections
    ("PORT_DUBLIN", "HUB_DUBLIN_M50", {
        "corridor": "Dublin Port Tunnel & M50", "distance_km": 18.5,
        "hgv_speed_kmh": 65.0, "road_type": "Motorway/Tunnel", "toll_eur": 10.0
    }),
    ("PORT_DUBLIN", "HUB_DUNDALK", {
        "corridor": "M1 North Corridor", "distance_km": 82.0,
        "hgv_speed_kmh": 85.0, "road_type": "Motorway", "toll_eur": 5.80
    }),

    # Dublin Hub to Regional Hubs
    ("HUB_DUBLIN_M50", "HUB_ATHLONE", {
        "corridor": "M4 / M6 Westbound", "distance_km": 118.0,
        "hgv_speed_kmh": 88.0, "road_type": "Motorway", "toll_eur": 5.40
    }),
    ("HUB_DUBLIN_M50", "HUB_LIMERICK", {
        "corridor": "M7 Southwest Corridor", "distance_km": 192.0,
        "hgv_speed_kmh": 88.0, "road_type": "Motorway", "toll_eur": 3.40
    }),
    ("HUB_DUBLIN_M50", "HUB_WATERFORD_INLAND", {
        "corridor": "M9 South Corridor", "distance_km": 156.0,
        "hgv_speed_kmh": 85.0, "road_type": "Motorway", "toll_eur": 3.40
    }),
    ("HUB_DUBLIN_M50", "PORT_ROSSLARE", {
        "corridor": "M11 / N11 Southeast Corridor", "distance_km": 158.0,
        "hgv_speed_kmh": 80.0, "road_type": "Motorway/National", "toll_eur": 3.40
    }),

    # Athlone Crossroads
    ("HUB_ATHLONE", "HUB_GALWAY", {
        "corridor": "M6 West Corridor", "distance_km": 86.0,
        "hgv_speed_kmh": 88.0, "road_type": "Motorway", "toll_eur": 3.40
    }),
    ("HUB_ATHLONE", "HUB_LIMERICK", {
        "corridor": "N62 / M7 Linking", "distance_km": 112.0,
        "hgv_speed_kmh": 75.0, "road_type": "National Primary", "toll_eur": 0.0
    }),

    # Cork & South/Southwest
    ("PORT_CORK", "HUB_CORK_INLAND", {
        "corridor": "N28 / Jack Lynch Tunnel", "distance_km": 16.0,
        "hgv_speed_kmh": 60.0, "road_type": "Dual Carriageway", "toll_eur": 0.0
    }),
    ("HUB_CORK_INLAND", "HUB_DUBLIN_M50", {
        "corridor": "M8 / M7 South-North Corridor", "distance_km": 248.0,
        "hgv_speed_kmh": 88.0, "road_type": "Motorway", "toll_eur": 6.80
    }),
    ("HUB_CORK_INLAND", "HUB_LIMERICK", {
        "corridor": "N20 Cork-Limerick Route", "distance_km": 98.0,
        "hgv_speed_kmh": 70.0, "road_type": "National Primary", "toll_eur": 0.0
    }),
    ("HUB_CORK_INLAND", "HUB_WATERFORD_INLAND", {
        "corridor": "N25 Southern Coastal Corridor", "distance_km": 118.0,
        "hgv_speed_kmh": 75.0, "road_type": "National Primary", "toll_eur": 2.20
    }),

    # Rosslare & Waterford Southeast connections
    ("PORT_ROSSLARE", "HUB_WATERFORD_INLAND", {
        "corridor": "N25 New Ross Bypass", "distance_km": 74.0,
        "hgv_speed_kmh": 78.0, "road_type": "National Primary/Bypass", "toll_eur": 2.20
    }),
    ("PORT_WATERFORD", "HUB_WATERFORD_INLAND", {
        "corridor": "N29 Port Access", "distance_km": 9.0,
        "hgv_speed_kmh": 60.0, "road_type": "Arterial Link", "toll_eur": 0.0
    }),
    ("HUB_WATERFORD_INLAND", "HUB_LIMERICK", {
        "corridor": "N24 Tipperary Valley Corridor", "distance_km": 128.0,
        "hgv_speed_kmh": 72.0, "road_type": "National Primary", "toll_eur": 0.0
    }),
]


class IrishFreightCorridorNetwork:
    """The road network as a NetworkX graph."""

    def __init__(self):
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        for node_id, attrs in NODES.items():
            self.graph.add_node(node_id, **attrs)

        for u, v, attrs in EDGES:
            # Driving time with no traffic, in hours
            free_flow_hours = attrs["distance_km"] / attrs["hgv_speed_kmh"]
            attrs["free_flow_hours"] = round(free_flow_hours, 3)
            self.graph.add_edge(u, v, **attrs)

    def get_shortest_route(
        self,
        origin: str,
        destination: str,
        weight: str = "distance_km"
    ) -> Dict[str, Any]:
        """
        Shortest (or quickest) route between two nodes.

        Args:
            origin: node ID, for example 'PORT_DUBLIN'
            destination: node ID, for example 'HUB_GALWAY'
            weight: 'distance_km' for the shortest route, 'free_flow_hours' for the quickest

        Returns:
            The nodes on the route, total distance, driving time, tolls and each road segment.
        """
        if origin not in self.graph:
            raise ValueError(f"Origin node {origin} not in graph.")
        if destination not in self.graph:
            raise ValueError(f"Destination node {destination} not in graph.")

        path = nx.shortest_path(self.graph, source=origin, target=destination, weight=weight)

        total_distance_km = 0.0
        total_driving_hours = 0.0
        total_toll_eur = 0.0
        segments = []

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_data = self.graph[u][v]
            total_distance_km += edge_data["distance_km"]
            total_driving_hours += edge_data["free_flow_hours"]
            total_toll_eur += edge_data.get("toll_eur", 0.0)
            segments.append({
                "from": u,
                "to": v,
                "corridor": edge_data.get("corridor"),
                "distance_km": edge_data["distance_km"],
                "driving_hours": edge_data["free_flow_hours"],
                "toll_eur": edge_data.get("toll_eur", 0.0)
            })

        return {
            "origin": origin,
            "destination": destination,
            "path_nodes": path,
            "total_distance_km": round(total_distance_km, 2),
            "total_driving_hours": round(total_driving_hours, 2),
            "total_toll_eur": round(total_toll_eur, 2),
            "segment_count": len(segments),
            "segments": segments,
        }

    def compute_distance_matrix(self) -> pd.DataFrame:
        """Shortest road distance in km between every pair of nodes."""
        node_list = list(self.graph.nodes)
        matrix = {node: {} for node in node_list}

        for u in node_list:
            for v in node_list:
                if u == v:
                    matrix[u][v] = 0.0
                else:
                    dist = nx.shortest_path_length(self.graph, source=u, target=v, weight="distance_km")
                    matrix[u][v] = round(dist, 1)

        return pd.DataFrame(matrix)
