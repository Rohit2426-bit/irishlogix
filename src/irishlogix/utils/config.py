"""
Truck and driving-rule settings for the Week 1 baseline.
The values are typical figures for Irish road freight and the EU driving-time rules.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

# Main Irish freight ports
MAJOR_PORTS = {
    "IEDUB": "Dublin",
    "IECRK": "Cork",
    "IERSS": "Rosslare",
    "IESHF": "Shannon Foynes",
    "IEWAT": "Waterford"
}

# Inland freight hubs
FREIGHT_HUBS = {
    "HUB_DUBLIN_M50": "Dublin M50 Logistics Hub (Ballymount/Southwest)",
    "HUB_ATHLONE": "Athlone Central Logistics Hub (Midlands M6)",
    "HUB_LIMERICK": "Limerick / Shannon Airport Freight Park (M18/M7)",
    "HUB_GALWAY": "Galway East Distribution Center (M6)",
    "HUB_WATERFORD": "Waterford Belview Logistics Center",
    "HUB_CORK_INLAND": "Cork Little Island Industrial Estate",
    "HUB_DUNDALK": "Dundalk Northern Corridor Gateway (M1/A1)"
}

@dataclass(frozen=True)
class VehicleParameters:
    """A 40 tonne Euro VI diesel articulated truck."""
    payload_capacity_tonnes: float = 24.0
    gross_vehicle_weight_tonnes: float = 40.0
    driving_fuel_consumption_l_per_km: float = 0.315   # 31.5 litres per 100 km
    idle_fuel_consumption_l_per_hr: float = 2.50       # litres per hour when idling at the gate
    diesel_emissions_factor_g_per_l: float = 2640.0    # 2.64 kg of CO2 per litre of diesel
    driver_hourly_wage_eur: float = 26.50              # typical Irish HGV driver pay per hour
    vehicle_operating_cost_per_km_eur: float = 0.48    # tyres, maintenance and insurance
    default_ets2_carbon_price_eur_per_tonne: float = 80.0  # default ETS2 price

@dataclass(frozen=True)
class RegulationEC561Rules:
    """EU driving-time rules, Regulation (EC) No 561/2006."""
    max_continuous_driving_hours: float = 4.5
    mandatory_break_duration_hours: float = 0.75       # 45 minutes
    max_daily_driving_hours: float = 9.0
    extended_daily_driving_hours: float = 10.0         # allowed twice a week
