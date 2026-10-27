"""
Daily port activity and congestion for Dublin and Rosslare.

Quarterly vessel arrivals and loaded Ro-Ro units come from the CSO (TBQ01, TBQ03). They are
spread over the days of each quarter with an assumed weekday profile, Irish public holidays,
random disruption days and a persistent congestion shock. The latent congestion index is
split into Low, Medium and High using thresholds fixed on the training period, which gives
the daily label that the port congestion model (C1) learns to predict one day ahead.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd

from . import assumptions as A


def easter_sunday(year: int) -> date:
    """Anonymous Gregorian algorithm."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def first_monday(year: int, month: int) -> date:
    d = date(year, month, 1)
    return d + timedelta(days=(7 - d.weekday()) % 7)


def last_monday(year: int, month: int) -> date:
    d = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year, 12, 31)
    return d - timedelta(days=d.weekday())


def irish_public_holidays(year: int) -> set:
    days = {date(year, 1, 1), date(year, 3, 17), date(year, 12, 25), date(year, 12, 26),
            easter_sunday(year) + timedelta(days=1), first_monday(year, 5), first_monday(year, 6),
            first_monday(year, 8), last_monday(year, 10)}
    if year >= 2023:  # St Brigid's Day: first Monday in February (or 1 Feb when it is a Friday)
        feb1 = date(year, 2, 1)
        days.add(feb1 if feb1.weekday() == 4 else first_monday(year, 2))
    return days


def build_calendar(start: str = A.HISTORY_START, end: str = A.TEST_END) -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="D")
    holidays = set().union(*(irish_public_holidays(y) for y in range(dates[0].year, dates[-1].year + 1)))
    cal = pd.DataFrame({"date": dates})
    cal["dow"] = cal["date"].dt.dayofweek
    cal["month"] = cal["date"].dt.month
    cal["year"] = cal["date"].dt.year
    cal["quarter"] = cal["date"].dt.year.astype(str) + "Q" + cal["date"].dt.quarter.astype(str)
    cal["is_holiday"] = cal["date"].dt.date.isin(holidays)
    return cal


def simulate_port_days(activity: pd.DataFrame, seed: int = 2026) -> pd.DataFrame:
    """
    Daily truth for each port in scope.

    Args:
        activity: CSO quarterly matrix (build_port_activity_matrix output).
        seed: random seed for the simulated daily variation.
    """
    rng = np.random.default_rng(seed)
    cal = build_calendar()
    profile = np.array(A.WEEKDAY_PROFILE) / np.mean(A.WEEKDAY_PROFILE)
    frames = []
    for port in A.PORTS:
        q = activity[activity["port"] == port].set_index("quarter")
        # Carry the last published quarter forward where a series has not been released yet.
        q = q[["vessel_arrivals", "roro_loaded_units", "gb_share"]].sort_index().ffill()
        df = cal.copy()
        df["port"] = port
        days_in_q = df.groupby("quarter")["date"].transform("count")
        weight = profile[df["dow"]] * np.where(df["is_holiday"], A.HOLIDAY_FACTOR, 1.0)
        weight = weight / df.assign(w=weight).groupby("quarter")["w"].transform("mean")
        q_arr = df["quarter"].map(q["vessel_arrivals"]).ffill()
        q_units = df["quarter"].map(q["roro_loaded_units"]).ffill()
        df["gb_share"] = df["quarter"].map(q["gb_share"]).ffill().bfill()

        lam = q_arr / days_in_q * weight
        df["scheduled_arrivals"] = rng.poisson(lam.clip(lower=0.1))
        ratio = np.sqrt(df["scheduled_arrivals"].clip(lower=1) / lam.clip(lower=0.1))
        df["roro_units"] = (q_units / days_in_q * weight * ratio * rng.lognormal(0, 0.08, len(df))).round()

        winter = df["date"].dt.quarter.isin([1, 4])
        p_dis = np.where(winter, A.DISRUPTION_PROB["winter"], A.DISRUPTION_PROB["summer"])
        df["disruption"] = rng.random(len(df)) < p_dis
        hit = rng.random(len(df)) < A.WARNING_HIT_RATE
        false_alarm = rng.random(len(df)) < A.WARNING_FALSE_ALARM
        df["disruption_warning"] = np.where(df["disruption"], hit, false_alarm)  # issued the evening before

        shocks = np.zeros(len(df))
        eps = rng.normal(0, A.SHOCK_SD, len(df))
        for t in range(1, len(df)):
            shocks[t] = A.SHOCK_PERSISTENCE * shocks[t - 1] + eps[t]
        train = df["date"] <= A.TRAIN_END
        capacity = df.loc[train, "roro_units"].quantile(0.95)
        df["utilisation"] = df["roro_units"] / capacity
        df["congestion_index"] = (A.UTILISATION_WEIGHT * df["utilisation"] + shocks
                                  + A.DISRUPTION_EFFECT * df["disruption"])
        lo, hi = df.loc[train, "congestion_index"].quantile([1 / 3, 2 / 3])
        df["congestion_class"] = pd.cut(df["congestion_index"], [-np.inf, lo, hi, np.inf],
                                        labels=["Low", "Medium", "High"]).astype(str)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
