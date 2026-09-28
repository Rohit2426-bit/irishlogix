"""
Unit tests for CSO data loader module.
"""

import pytest
import pandas as pd
from pathlib import Path
from irishlogix.data.cso_loader import CSODataLoader

def test_cso_cache_directory_created(tmp_path):
    loader = CSODataLoader(cache_dir=tmp_path / "cso_test")
    assert loader.cache_dir.exists()

def test_cso_arrivals_filtering():
    loader = CSODataLoader()
    # Ensure cached or live fetch works and returns DataFrame
    df = loader.get_port_arrivals()
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "port" in df.columns
    assert "value" in df.columns
    # Check that key ports are present
    ports = df["port"].unique()
    assert "Dublin" in ports or "IEDUB" in ports

def test_cso_port_activity_matrix():
    loader = CSODataLoader()
    matrix = loader.build_port_activity_matrix()
    assert isinstance(matrix, pd.DataFrame)
    assert "year" in matrix.columns
    assert "port" in matrix.columns
    assert "vessel_arrivals" in matrix.columns
