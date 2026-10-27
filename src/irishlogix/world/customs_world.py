"""
Customs clearance and consignment generation.

Clearance time depends on observable consignment features (origin, commodity, whether the
declaration was lodged before arrival, trusted-trader status, night arrival, port congestion)
plus random documentary and physical checks that cannot be known in advance. The customs
model (C2) learns the predictable part; the random checks remain irreducible noise.
"""

import numpy as np
import pandas as pd

from . import assumptions as A

COMMODITIES = list(A.COMMODITY_MIX)
COMMODITY_P = np.array(list(A.COMMODITY_MIX.values()))


def sample_features(rng: np.random.Generator, n: int, port: str, day: pd.Timestamp, gb_share: float,
                    hours: tuple = (0.0, 24.0)) -> pd.DataFrame:
    """Observable features of n consignments arriving at one port on one day."""
    gb = rng.random(n) < gb_share
    vessel_hour = rng.uniform(*hours, n).round(2)
    return pd.DataFrame({
        "date": day, "port": port, "dow": day.dayofweek, "month": day.month,
        "origin_gb": gb,
        "commodity": rng.choice(COMMODITIES, n, p=COMMODITY_P),
        "prelodged": np.where(gb, rng.random(n) < A.PRELODGED_PROB, True),
        "aeo": rng.random(n) < A.AEO_PROB,
        "vessel_hour": vessel_hour,
        "night": (vessel_hour >= 22) | (vessel_hour < 6),
    })


def true_clearance(rng: np.random.Generator, f: pd.DataFrame, congestion_class: pd.Series,
                   check_scale: float = 1.0) -> pd.DataFrame:
    """
    Realised clearance hours for each consignment.

    Args:
        check_scale: multiplies the documentary and physical check probabilities (sensitivity analysis).
    """
    n = len(f)
    base = rng.lognormal(np.log(A.GB_BASE_MEDIAN_HOURS), A.GB_BASE_SPREAD, n)
    base *= np.where(f["prelodged"], 1.0, A.NOT_PRELODGED_FACTOR)
    base *= np.where(f["aeo"], A.AEO_FACTOR, 1.0)
    base *= np.where(f["night"], A.NIGHT_FACTOR, 1.0)
    base *= np.where(np.asarray(congestion_class) == "High", A.HIGH_CONGESTION_FACTOR, 1.0)
    p_phys = f["commodity"].map(A.PHYSICAL_CHECK_PROB).to_numpy() * check_scale
    p_doc = np.full(n, A.DOCUMENT_CHECK_PROB * check_scale) * np.where(f["prelodged"], 1.0, 1.5)
    physical = rng.random(n) < p_phys
    document = rng.random(n) < p_doc
    gb_hours = (base + document * rng.uniform(*A.DOCUMENT_CHECK_HOURS, n)
                + physical * rng.uniform(*A.PHYSICAL_CHECK_HOURS, n))
    eu_hours = rng.uniform(*A.EU_CLEARANCE_HOURS, n)
    out = pd.DataFrame({
        "clearance_hours": np.where(f["origin_gb"], gb_hours, eu_hours).round(3),
        "document_check": f["origin_gb"].to_numpy() & document,
        "physical_check": f["origin_gb"].to_numpy() & physical,
    }, index=f.index)
    return out


def customs_history(port_days: pd.DataFrame, per_port_day: int = 12, seed: int = 7,
                    start: str = A.CUSTOMS_START, end: str = A.TEST_END) -> pd.DataFrame:
    """Historical consignment records used to train and test C2 (post-Brexit period only)."""
    rng = np.random.default_rng(seed)
    days = port_days[(port_days["date"] >= start) & (port_days["date"] <= end)]
    frames = []
    for _, d in days.iterrows():
        f = sample_features(rng, per_port_day, d["port"], d["date"], d["gb_share"])
        f["congestion_class"] = d["congestion_class"]
        frames.append(pd.concat([f, true_clearance(rng, f, f["congestion_class"])], axis=1))
    return pd.concat(frames, ignore_index=True)


def day_instance(port_days: pd.DataFrame, day: pd.Timestamp, seed: int,
                 n: int = A.CONSIGNMENTS_PER_DAY, check_scale: float = 1.0) -> pd.DataFrame:
    """
    One planning day for the haulier: n import consignments with their observable features,
    deadlines, and the hidden truth (unload time, clearance time, queue draw, congestion class)
    used only when a plan is executed. All planners see the same instance (common random numbers).
    """
    rng = np.random.default_rng(seed)
    today = port_days[port_days["date"] == day].set_index("port")
    share = today.loc[A.PORTS, "roro_units"] / today.loc[A.PORTS, "roro_units"].sum()
    ports = rng.choice(A.PORTS, n, p=share.to_numpy())
    rows = []
    for k, port in enumerate(ports):
        f = sample_features(rng, 1, port, day, today.loc[port, "gb_share"], hours=A.VESSEL_HOURS)
        f["consignment_id"] = f"{day:%Y%m%d}-{k + 1}"
        f["port_node"] = A.PORT_NODES[port]
        f["destination"] = rng.choice(A.DESTINATION_HUBS)
        f["deadline_hour"] = (f["vessel_hour"] + rng.uniform(*A.DELIVERY_WINDOW_HOURS)).round(2)
        f["true_congestion_class"] = today.loc[port, "congestion_class"]
        f["true_unload_hours"] = rng.lognormal(np.log(A.UNLOAD_MEDIAN_HOURS[port]), A.UNLOAD_SPREAD)
        f = pd.concat([f, true_clearance(rng, f, f["true_congestion_class"], check_scale)], axis=1)
        f["queue_draw"] = rng.random()   # uniform draw mapped to the realised gate queue
        rows.append(f)
    return pd.concat(rows, ignore_index=True).rename(columns={"clearance_hours": "true_clearance_hours"})
