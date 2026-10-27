"""
Tests for the simulation world (calendar, port days, customs).
"""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from irishlogix.world import assumptions as A
from irishlogix.world.customs_world import day_instance, sample_features, true_clearance
from irishlogix.world.port_world import irish_public_holidays, simulate_port_days


@pytest.fixture(scope="module")
def port_days():
    return simulate_port_days(pd.read_csv("data/processed/cso_port_activity_matrix.csv"))


def test_irish_holidays_2025():
    h = irish_public_holidays(2025)
    assert date(2025, 4, 21) in h      # Easter Monday
    assert date(2025, 2, 3) in h       # St Brigid's Day
    assert date(2025, 10, 27) in h     # October bank holiday


def test_congestion_classes_balanced_in_training(port_days):
    train = port_days[port_days["date"] <= A.TRAIN_END]
    shares = train.groupby("port")["congestion_class"].value_counts(normalize=True)
    assert shares.between(0.30, 0.37).all()
    assert port_days["congestion_class"].isin(["Low", "Medium", "High"]).all()


def test_eu_clearance_is_short_and_checks_scale():
    rng = np.random.default_rng(0)
    f = sample_features(rng, 2000, "Dublin", pd.Timestamp("2025-03-03"), gb_share=0.5)
    cls = pd.Series(["Medium"] * len(f))
    out = true_clearance(np.random.default_rng(1), f, cls)
    assert out.loc[~f["origin_gb"], "clearance_hours"].max() <= A.EU_CLEARANCE_HOURS[1]
    none = true_clearance(np.random.default_rng(1), f, cls, check_scale=0.0)
    assert not none["physical_check"].any() and not none["document_check"].any()


def test_day_instance_reproducible(port_days):
    day = pd.Timestamp("2025-03-12")
    a = day_instance(port_days, day, seed=5)
    b = day_instance(port_days, day, seed=5)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == A.CONSIGNMENTS_PER_DAY
    c = day_instance(port_days, day, seed=5, check_scale=1.5)
    assert (a["vessel_hour"] == c["vessel_hour"]).all()   # common random numbers across scenarios
