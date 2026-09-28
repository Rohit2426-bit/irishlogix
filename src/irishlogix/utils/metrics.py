"""
Core operational, financial, and environmental metrics calculator for Irish freight routes.
"""

from typing import Dict, Any
from .config import VehicleParameters, RegulationEC561Rules

def calculate_trip_metrics(
    distance_km: float,
    driving_hours: float,
    idle_waiting_hours: float,
    diesel_price_eur_per_litre: float = 1.75,
    ets2_price_eur_per_tonne: float = 80.0,
    vehicle: VehicleParameters = VehicleParameters(),
    rules: RegulationEC561Rules = RegulationEC561Rules()
) -> Dict[str, Any]:
    """
    Computes comprehensive operational, economic, and carbon metrics for a freight trip.

    Args:
        distance_km: Transit road distance in kilometers.
        driving_hours: Active vehicle driving time in hours.
        idle_waiting_hours: Idle time spent queueing at port gates or awaiting customs clearance.
        diesel_price_eur_per_litre: Current pump/bulk commercial diesel price in EUR.
        ets2_price_eur_per_tonne: EU ETS2 carbon price per tonne of CO2.
        vehicle: Vehicle parameter dataclass.
        rules: EC 561/2006 driver regulation rules.

    Returns:
        Dictionary containing granular operational KPIs.
    """
    # Fuel calculations
    driving_fuel_litres = distance_km * vehicle.driving_fuel_consumption_l_per_km
    idle_fuel_litres = idle_waiting_hours * vehicle.idle_fuel_consumption_l_per_hr
    total_fuel_litres = driving_fuel_litres + idle_fuel_litres

    # Carbon emissions (grams and kg)
    total_carbon_emissions_g = total_fuel_litres * vehicle.diesel_emissions_factor_g_per_l
    total_carbon_emissions_kg = total_carbon_emissions_g / 1000.0

    # Carbon intensity per kilometer (gCO2e / km)
    carbon_intensity_g_per_km = (
        (total_carbon_emissions_g / distance_km) if distance_km > 0 else 0.0
    )

    # Financial costs
    driver_wage_cost_eur = (driving_hours + idle_waiting_hours) * vehicle.driver_hourly_wage_eur
    vehicle_running_cost_eur = distance_km * vehicle.vehicle_operating_cost_per_km_eur
    fuel_cost_eur = total_fuel_litres * diesel_price_eur_per_litre

    # ETS2 Carbon cost (€ = kg CO2 * (€ / 1000 kg))
    ets2_carbon_cost_eur = total_carbon_emissions_kg * (ets2_price_eur_per_tonne / 1000.0)

    total_operational_cost_eur = (
        driver_wage_cost_eur + vehicle_running_cost_eur + fuel_cost_eur + ets2_carbon_cost_eur
    )

    # Regulatory compliance (EC 561/2006)
    requires_mandatory_rest = driving_hours > rules.max_continuous_driving_hours
    rest_break_hours = rules.mandatory_break_duration_hours if requires_mandatory_rest else 0.0
    total_trip_elapsed_hours = driving_hours + idle_waiting_hours + rest_break_hours
    exceeds_daily_limit = driving_hours > rules.max_daily_driving_hours

    return {
        "distance_km": round(distance_km, 2),
        "driving_hours": round(driving_hours, 2),
        "idle_waiting_hours": round(idle_waiting_hours, 2),
        "rest_break_hours": round(rest_break_hours, 2),
        "total_trip_elapsed_hours": round(total_trip_elapsed_hours, 2),
        "driving_fuel_litres": round(driving_fuel_litres, 2),
        "idle_fuel_litres": round(idle_fuel_litres, 2),
        "total_fuel_litres": round(total_fuel_litres, 2),
        "total_carbon_emissions_kg": round(total_carbon_emissions_kg, 2),
        "carbon_intensity_g_per_km": round(carbon_intensity_g_per_km, 2),
        "driver_wage_cost_eur": round(driver_wage_cost_eur, 2),
        "vehicle_running_cost_eur": round(vehicle_running_cost_eur, 2),
        "fuel_cost_eur": round(fuel_cost_eur, 2),
        "ets2_carbon_cost_eur": round(ets2_carbon_cost_eur, 2),
        "total_operational_cost_eur": round(total_operational_cost_eur, 2),
        "ec561_break_required": requires_mandatory_rest,
        "ec561_daily_limit_exceeded": exceeds_daily_limit,
    }
