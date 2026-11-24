"""Truck settings and trip figures for the Week 1 baseline."""

from .config import MAJOR_PORTS, FREIGHT_HUBS, VehicleParameters, RegulationEC561Rules
from .metrics import calculate_trip_metrics

__all__ = [
    "MAJOR_PORTS",
    "FREIGHT_HUBS",
    "VehicleParameters",
    "RegulationEC561Rules",
    "calculate_trip_metrics",
]
