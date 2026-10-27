"""
Route options, speeds and the fuel/CO2 model used by the C3 optimiser.

Fuel use per km follows the structure of the Pollution-Routing Problem model (Bektaş and
Laporte, 2011): an engine term that falls with speed, a mass term that grows with load, and
an aerodynamic term that grows with speed squared. The shares of the three terms at 85 km/h
for a laden 40-tonne truck (9%, 73%, 18%) and the empty-truck mass are assumptions, and the
curve is scaled to the baseline consumption in VehicleParameters.
"""

from dataclasses import dataclass
from functools import lru_cache
from itertools import islice
from typing import List, Tuple

import networkx as nx

from ..network.corridor_network import IrishFreightCorridorNetwork
from ..utils.config import VehicleParameters

REF_SPEED = 85.0
SHARE_ENGINE, SHARE_MASS, SHARE_AERO = 0.09, 0.73, 0.18
LADEN_TONNES, EMPTY_TONNES = 40.0, 15.0
ECO_SPEED_CAP = 78.0
K_PATHS = 3
VEHICLE = VehicleParameters()


def fuel_per_km(speed_kmh: float, laden: bool) -> float:
    mass = LADEN_TONNES if laden else EMPTY_TONNES
    factor = (SHARE_ENGINE * REF_SPEED / speed_kmh + SHARE_MASS * mass / LADEN_TONNES
              + SHARE_AERO * (speed_kmh / REF_SPEED) ** 2)
    return VEHICLE.driving_fuel_consumption_l_per_km * factor


@dataclass(frozen=True)
class RouteOption:
    nodes: Tuple[str, ...]
    eco: bool
    distance_km: float
    hours: float
    toll_eur: float
    fuel_laden_l: float
    fuel_empty_l: float
    label: str


_NET = IrishFreightCorridorNetwork()
GRAPH: nx.Graph = _NET.graph


def _leg_option(path: List[str], eco: bool) -> RouteOption:
    dist = hours = toll = fl = fe = 0.0
    for u, v in zip(path[:-1], path[1:]):
        e = GRAPH[u][v]
        speed = min(e["hgv_speed_kmh"], ECO_SPEED_CAP) if eco else e["hgv_speed_kmh"]
        dist += e["distance_km"]
        hours += e["distance_km"] / speed
        toll += e["toll_eur"]
        fl += e["distance_km"] * fuel_per_km(speed, True)
        fe += e["distance_km"] * fuel_per_km(speed, False)
    label = " > ".join(n.split("_", 1)[1].title() for n in path) + (" (eco speed)" if eco else "")
    return RouteOption(tuple(path), eco, dist, hours, toll, fl, fe, label)


@lru_cache(maxsize=None)
def route_options(origin: str, destination: str) -> Tuple[RouteOption, ...]:
    """Up to K_PATHS shortest simple paths, each at standard and eco speed."""
    if origin == destination:
        return (RouteOption((origin,), False, 0.0, 0.0, 0.0, 0.0, 0.0, "No travel"),)
    paths = list(islice(nx.shortest_simple_paths(GRAPH, origin, destination, weight="distance_km"), K_PATHS))
    opts = []
    for p in paths:
        opts.append(_leg_option(p, eco=False))
        if any(GRAPH[u][v]["hgv_speed_kmh"] > ECO_SPEED_CAP for u, v in zip(p[:-1], p[1:])):
            opts.append(_leg_option(p, eco=True))
    return tuple(opts)


@lru_cache(maxsize=None)
def fastest(origin: str, destination: str) -> RouteOption:
    """Empty repositioning legs use the fastest standard-speed option."""
    return min((o for o in route_options(origin, destination) if not o.eco), key=lambda o: o.hours)


@lru_cache(maxsize=None)
def shortest(origin: str, destination: str) -> RouteOption:
    """The spreadsheet planner's choice: shortest distance at standard speed."""
    return route_options(origin, destination)[0]
