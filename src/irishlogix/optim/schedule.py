"""
Day schedule for a small fleet: timing, EC 561/2006 breaks, costs and CO2.

The same routine is used twice. At planning time it receives the planner's delay estimates and
sets the target arrival time at each port. At execution time it receives the true delays and
replays the fixed plan, so every planner is judged on the same realised day.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

from ..utils.config import RegulationEC561Rules, VehicleParameters
from ..world import assumptions as A
from .routes import fastest, route_options

VEH = VehicleParameters()
RULES = RegulationEC561Rules()
DIESEL_EUR_PER_L = 1.75
MAX_DUTY_HOURS = 13.0                 # 24 h minus the 11 h regular daily rest
VIOLATION_PENALTY_EUR_PER_HOUR = 1000.0


def queue_factor(offset_hours: float) -> float:
    """Extra gate queueing when arriving close to vessel discharge."""
    return 1.0 + A.DISCHARGE_PEAK_EXTRA * math.exp(-max(offset_hours, 0.0) / A.DISCHARGE_PEAK_DECAY_HOURS)


@dataclass
class Delays:
    """Delay information for each consignment (estimates when planning, truth when executing)."""
    ready_after_vessel: np.ndarray   # hours from vessel arrival until the trailer is released
    queue_base: np.ndarray           # mean gate queue before the discharge-peak factor (hours)
    queue_noise: np.ndarray          # multiplier: 1 when planning, realised lognormal draw when executing


@dataclass
class Plan:
    trucks: List[List[int]]                 # consignment indices in visiting order, per truck
    route_idx: Dict[int, int]               # chosen laden route option per consignment
    target_arrival: Dict[int, float]        # planned port arrival time (hour of day)


def simulate(plan: Plan, cons: dict, delays: Delays, set_targets: bool) -> dict:
    """
    Simulate the day. With set_targets=True the plan's target arrivals are (re)computed from the
    delay estimates; otherwise the given targets are kept and only pushed later if a truck is late.
    """
    v, dl, ports, dests = cons["vessel_hour"], cons["deadline_hour"], cons["port_node"], cons["destination"]
    per = {}
    totals = dict(cost_ex_carbon=0.0, co2_kg=0.0, km=0.0, idle_h=0.0, late_h=0.0, viol_h=0.0,
                  wage=0.0, fuel_l=0.0, tolls=0.0, drive_h=0.0, duty_h=0.0, breaks=0)
    for seq in plan.trucks:
        if not seq:
            continue
        loc, t = A.DEPOT, None
        drive_since_break = drive_total = km = fuel = tolls = idle_total = late_total = 0.0
        breaks = 0
        start = None
        for i in seq:
            empty = fastest(loc, ports[i])
            earliest = (t if t is not None else -1e9) + empty.hours
            if set_targets:
                ready = v[i] + delays.ready_after_vessel[i]
                q_est = delays.queue_base[i] * queue_factor(delays.ready_after_vessel[i])
                plan.target_arrival[i] = ready - q_est
            arrive = max(plan.target_arrival[i], earliest if t is not None else plan.target_arrival[i])
            leave_prev = arrive - empty.hours
            if start is None:
                start = leave_prev
            # Break before the empty leg if needed (EC 561/2006: 45 min after 4.5 h of driving).
            if drive_since_break + empty.hours > RULES.max_continuous_driving_hours:
                arrive += RULES.mandatory_break_duration_hours
                drive_since_break, breaks = 0.0, breaks + 1
            drive_since_break += empty.hours
            drive_total += empty.hours
            km += empty.distance_km
            fuel += empty.fuel_empty_l
            tolls += empty.toll_eur
            q = delays.queue_base[i] * queue_factor(arrive - v[i]) * delays.queue_noise[i]
            ready = v[i] + delays.ready_after_vessel[i]
            wait_release = max(0.0, ready - (arrive + q))
            idle = q + wait_release
            pickup = arrive + idle
            opt = route_options(ports[i], dests[i])[plan.route_idx[i]]
            depart = pickup
            if drive_since_break + opt.hours > RULES.max_continuous_driving_hours:
                depart += RULES.mandatory_break_duration_hours
                drive_since_break, breaks = 0.0, breaks + 1
            deliver = depart + opt.hours
            drive_since_break += opt.hours
            drive_total += opt.hours
            km += opt.distance_km
            fuel += opt.fuel_laden_l + idle * VEH.idle_fuel_consumption_l_per_hr
            tolls += opt.toll_eur
            late = max(0.0, deliver - dl[i])
            idle_total += idle
            late_total += late
            per[i] = dict(arrive=arrive, queue=q, wait_release=wait_release, idle=idle,
                          deliver=deliver, late=late, route=opt.label, eco=opt.eco)
            loc, t = dests[i], deliver
        back = fastest(loc, A.DEPOT)
        end = t
        if drive_since_break + back.hours > RULES.max_continuous_driving_hours:
            end += RULES.mandatory_break_duration_hours
            breaks += 1
        end += back.hours
        drive_total += back.hours
        km += back.distance_km
        fuel += back.fuel_empty_l
        tolls += back.toll_eur
        duty = end - start
        viol = max(0.0, drive_total - RULES.max_daily_driving_hours) + max(0.0, duty - MAX_DUTY_HOURS)
        wage = duty * VEH.driver_hourly_wage_eur
        cost = (wage + km * VEH.vehicle_operating_cost_per_km_eur + fuel * DIESEL_EUR_PER_L + tolls
                + late_total * A.LATENESS_PENALTY_EUR_PER_HOUR)
        totals["cost_ex_carbon"] += cost
        totals["co2_kg"] += fuel * VEH.diesel_emissions_factor_g_per_l / 1000.0
        for k, val in (("km", km), ("idle_h", idle_total), ("late_h", late_total), ("viol_h", viol),
                       ("wage", wage), ("fuel_l", fuel), ("tolls", tolls), ("drive_h", drive_total),
                       ("duty_h", duty), ("breaks", breaks)):
            totals[k] += val
    totals["objective_cost"] = totals["cost_ex_carbon"] + VIOLATION_PENALTY_EUR_PER_HOUR * totals["viol_h"]
    totals["g_co2_per_km"] = 1000.0 * totals["co2_kg"] / totals["km"] if totals["km"] else 0.0
    return {"totals": totals, "per_consignment": per}


def total_cost(totals: dict, ets2_eur_per_tonne: float) -> float:
    """Operating cost including the ETS2 carbon cost at a given price."""
    return totals["cost_ex_carbon"] + ets2_eur_per_tonne * totals["co2_kg"] / 1000.0
