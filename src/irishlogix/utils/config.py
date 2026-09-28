"""
Configuration parameters for IrishLogix freight optimization and delay analytics.
Grounded in Irish transport statistics and EU road freight regulatory standards.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

# Key Irish Freight Ports
MAJOR_PORTS = {
    "IEDUB": "Dublin",
    "IECRK": "Cork",
    "IERSS": "Rosslare",
    "IESHF": "Shannon Foynes",
    "IEWAT": "Waterford"
}

# Key Inland Distribution Centers and Regional Freight Hubs
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
    """Standard 40-tonne Euro VI Articulated Diesel HGV specifications."""
    payload_capacity_tonnes: float = 24.0
    gross_vehicle_weight_tonnes: float = 40.0
    driving_fuel_consumption_l_per_km: float = 0.315   # 31.5 L/100km at standard cruising
    idle_fuel_consumption_l_per_hr: float = 2.50       # 2.5 L/hr engine idling at terminal/gate
    diesel_emissions_factor_g_per_l: float = 2640.0    # 2.64 kg CO2e / Litre diesel
    driver_hourly_wage_eur: float = 26.50              # Standard Irish HGV driver gross rate
    vehicle_operating_cost_per_km_eur: float = 0.48    # Tyres, wear, maintenance, insurance
    default_ets2_carbon_price_eur_per_tonne: float = 80.0  # EU ETS2 carbon price baseline

@dataclass(frozen=True)
class RegulationEC561Rules:
    """EU Regulation (EC) No 561/2006 on driving times and rest periods."""
    max_continuous_driving_hours: float = 4.5
    mandatory_break_duration_hours: float = 0.75       # 45 minutes
    max_daily_driving_hours: float = 9.0
    extended_daily_driving_hours: float = 10.0         # Allowed twice weekly
