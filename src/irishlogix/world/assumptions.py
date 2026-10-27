"""
Assumed parameters of the IrishLogix simulation world.

The world is semi-synthetic: quarterly levels come from official CSO statistics, while the
daily and within-day behaviour below is assumed, because daily port and customs data are not
public. Every value here is a modelling assumption, is reported in the Configuration Manual,
and the most influential ones are varied in the sensitivity analysis.
"""

# Ports in scope: Dublin and Rosslare carry about 98% of loaded Ro-Ro freight units (CSO TBQ03).
PORTS = ["Dublin", "Rosslare"]
PORT_NODES = {"Dublin": "PORT_DUBLIN", "Rosslare": "PORT_ROSSLARE"}

# Daily traffic shape within a week (Mon..Sun); rescaled to mean 1 when used.
WEEKDAY_PROFILE = [1.10, 1.10, 1.05, 1.05, 1.05, 0.85, 0.80]
HOLIDAY_FACTOR = 0.70

# Disruption days (storms, system outages): probability per day by season, and warning quality.
DISRUPTION_PROB = {"winter": 0.05, "summer": 0.015}      # winter = Q1 and Q4
WARNING_HIT_RATE = 0.70                                     # disruption announced the day before
WARNING_FALSE_ALARM = 0.02

# Latent congestion index: utilisation + persistent shock + disruption.
SHOCK_PERSISTENCE = 0.60
SHOCK_SD = 0.35
DISRUPTION_EFFECT = 1.20
UTILISATION_WEIGHT = 2.0

# Gate queue (hours) by congestion class at each port, and lognormal spread.
QUEUE_MEAN_HOURS = {
    "Dublin": {"Low": 0.25, "Medium": 0.60, "High": 1.40},
    "Rosslare": {"Low": 0.20, "Medium": 0.45, "High": 1.00},
}
QUEUE_SPREAD = 0.45
# Extra queueing when a truck arrives just as a vessel discharges; decays with hours after arrival.
DISCHARGE_PEAK_EXTRA = 1.0
DISCHARGE_PEAK_DECAY_HOURS = 1.0

# Time from vessel arrival until the trailer is unloaded (hours, lognormal median and spread).
UNLOAD_MEDIAN_HOURS = {"Dublin": 1.0, "Rosslare": 0.8}
UNLOAD_SPREAD = 0.30

# Consignment mix (assumed) and customs behaviour for GB-origin freight.
COMMODITY_MIX = {"General merchandise": 0.55, "Agrifood (SPS)": 0.30, "Machinery and parts": 0.15}
PRELODGED_PROB = 0.85          # customs declaration lodged before arrival
AEO_PROB = 0.30                # trusted trader (Authorised Economic Operator)
EU_CLEARANCE_HOURS = (0.05, 0.20)
GB_BASE_MEDIAN_HOURS = 0.50
GB_BASE_SPREAD = 0.35
NOT_PRELODGED_FACTOR = 2.2
AEO_FACTOR = 0.6
NIGHT_FACTOR = 1.3             # vessel arriving 22:00 to 06:00
HIGH_CONGESTION_FACTOR = 1.2
PHYSICAL_CHECK_PROB = {"Agrifood (SPS)": 0.15, "General merchandise": 0.04, "Machinery and parts": 0.04}
PHYSICAL_CHECK_HOURS = (1.5, 4.0)
DOCUMENT_CHECK_PROB = 0.15
DOCUMENT_CHECK_HOURS = (0.5, 1.5)

# Planning instances: one small haulier with a depot at the Dublin M50 hub.
DEPOT = "HUB_DUBLIN_M50"
FLEET_SIZE = 4
CONSIGNMENTS_PER_DAY = 5
DESTINATION_HUBS = ["HUB_DUBLIN_M50", "HUB_ATHLONE", "HUB_LIMERICK", "HUB_GALWAY",
                    "HUB_WATERFORD_INLAND", "HUB_DUNDALK", "HUB_CORK_INLAND"]
VESSEL_HOURS = (5.0, 18.0)       # vessel arrival window used for daytime haulage planning
DELIVERY_WINDOW_HOURS = (7.0, 11.0)
LATENESS_PENALTY_EUR_PER_HOUR = 150.0   # assumed customer penalty for late delivery

# Study periods.
HISTORY_START = "2017-01-01"
CUSTOMS_START = "2021-01-01"     # GB customs controls apply after the end of the Brexit transition
TRAIN_END = "2023-12-31"
VALID_END = "2024-12-31"
TEST_END = "2026-06-30"
