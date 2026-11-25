"""Tests for the LSTM input data: correct shape and no information from the target day."""

import numpy as np
import pandas as pd
import pytest

from irishlogix.models import c1_congestion as c1
from irishlogix.models import neural
from irishlogix.world.port_world import simulate_port_days


@pytest.fixture(scope="module")
def data():
    port_days = simulate_port_days(pd.read_csv("data/processed/cso_port_activity_matrix.csv"))
    feat = c1.build_features(port_days).head(200)
    return port_days, feat


def test_sequence_shapes(data):
    port_days, feat = data
    seq, nxt = neural.sequence_data(port_days, feat)
    assert seq.shape == (len(feat), neural.SEQ_LEN, len(neural.SEQ_COLS))
    assert nxt.shape == (len(feat), len(neural.NEXT_COLS))


def test_sequence_ends_the_day_before(data):
    port_days, feat = data
    seq, _ = neural.sequence_data(port_days, feat)
    row = feat.iloc[50]
    d = port_days[port_days["port"] == row["port"]].sort_values("date").reset_index(drop=True)
    i = d.index[d["date"] == row["date"]][0]
    # the last step of the sequence is the previous day, never the target day
    assert np.isclose(seq[50, -1, 0], d.loc[i - 1, "congestion_index"])
    assert np.isclose(seq[50, 0, 0], d.loc[i - neural.SEQ_LEN, "congestion_index"])
