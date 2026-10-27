"""
Unit tests for the CSO data loader.
"""

import pandas as pd

from irishlogix.data.cso_loader import ARRIVALS, CSODataLoader


def test_cso_cache_directory_created(tmp_path):
    loader = CSODataLoader(cache_dir=tmp_path / "cso_test")
    assert loader.cache_dir.exists()


def test_arrivals_use_vessel_count_only():
    df = CSODataLoader().get_port_arrivals()
    assert len(df) > 0
    assert set(df["statistic"]) == {ARRIVALS}
    assert "Dublin" in set(df["port"])


def test_port_activity_matrix_has_plausible_values():
    m = CSODataLoader().build_port_activity_matrix()
    for col in ["vessel_arrivals", "roro_loaded_units", "gb_share"]:
        assert col in m.columns
    dublin = m[(m["port"] == "Dublin") & (m["year"] >= 2023)]
    # Dublin handles roughly 1,500 to 2,000 vessel arrivals and 150k to 260k loaded Ro-Ro units per quarter.
    assert dublin["vessel_arrivals"].dropna().between(1000, 2500).all()
    assert dublin["roro_loaded_units"].between(150_000, 260_000).all()
    assert m["gb_share"].dropna().between(0, 1).all()
