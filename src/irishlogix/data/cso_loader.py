"""
Automated Data Loader and Preprocessor for Irish Central Statistics Office (CSO)
Maritime and Port Traffic Datasets.

Fetches open data via the CSO PxStat REST API and builds the quarterly port activity
matrix used to calibrate the IrishLogix simulation world and the port congestion model (C1).

Each table holds several statistics (for example counts and tonnages), so every query
below selects one statistic code explicitly rather than summing across them.
"""

import io
import logging
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

CSO_API_BASE_URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset"

# Recognised CSO port traffic tables (Statistics of Port Traffic, quarterly).
CSO_TABLES = {
    "TBQ01": "Vessel arrivals and gross tonnage by port",
    "TBQ03": "Ro-Ro passenger and freight vehicles/trailers handled by port and direction",
    "TBQ04": "Lo-Lo container units (number and TEU) by port and direction",
    "TBQ05": "Goods handled by port and region of trade, 2017 to 2023 (legacy series)",
    "TBQ07": "Goods handled by port and region of trade, 2020 onwards",
}

# Statistic codes used in this project.
ARRIVALS = "TBQ01C01"            # Arrivals (number of vessels)
RORO_LOADED_UNITS = "TBQ03C05"   # Loaded freight vehicles/trailers handled (number)
RORO_EMPTY_UNITS = "TBQ03C07"    # Empty freight vehicles/trailers handled (number)
LOLO_TOTAL_UNITS = "TBQ04C01"    # Total container units (number)

# Ro-Ro freight ports in scope (Dublin and Rosslare carry about 98% of loaded Ro-Ro units).
RORO_PORTS = ["Dublin", "Rosslare"]
STUDY_PORTS = ["Dublin", "Rosslare", "Cork"]

GB_REGION_LABELS = ["Foreign trade: Great Britain and Northern Ireland"]
EU_REGION_LABELS = ["Foreign trade: Other EU", "Foreign trade: EU27 2020, excl Ireland"]

DEFAULT_CACHE_DIR = Path("data/raw/cso")


class CSODataLoader:
    """Manages downloading, local caching, and parsing of CSO port traffic tables."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_raw_table(self, table_code: str, force_download: bool = False) -> str:
        """Retrieves the raw CSV text for a CSO table, using the local cache when available."""
        table_code = table_code.upper()
        if table_code not in CSO_TABLES:
            logger.warning(f"Table code {table_code} not in standard catalog, proceeding anyway.")

        cache_file = self.cache_dir / f"{table_code}.csv"
        if cache_file.exists() and not force_download:
            logger.info(f"Loading {table_code} from local cache: {cache_file}")
            with open(cache_file, "r", encoding="utf-8-sig") as f:
                return f.read()

        url = f"{CSO_API_BASE_URL}/{table_code}/CSV/1.0/en"
        logger.info(f"Downloading table {table_code} from CSO PxStat API: {url}")
        req = urllib.request.Request(
            url, headers={"User-Agent": "IrishLogix-ResearchPracticum-NCI/1.0 (academic data ingestion)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                raw_text = response.read().decode("utf-8-sig")
            with open(cache_file, "w", encoding="utf-8-sig") as f:
                f.write(raw_text)
            logger.info(f"Cached {len(raw_text)} chars to {cache_file}")
            return raw_text
        except urllib.error.URLError as e:
            logger.error(f"Failed to fetch {table_code} from CSO API: {e}")
            if cache_file.exists():
                logger.info(f"Falling back to stale local cache for {table_code}")
                with open(cache_file, "r", encoding="utf-8-sig") as f:
                    return f.read()
            raise

    def load_table_df(self, table_code: str, force_download: bool = False) -> pd.DataFrame:
        """Loads a table and returns a tidy DataFrame with standardised column names."""
        df = pd.read_csv(io.StringIO(self.fetch_raw_table(table_code, force_download=force_download)))
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        if "quarter" in df.columns:
            df["year"] = df["quarter"].str[:4].astype(int)
            df["quarter_num"] = df["quarter"].str[-1].astype(int)
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"].astype(str).str.replace(",", ""), errors="coerce")
        return df

    # ------------------------------------------------------------------ single tables
    def get_port_arrivals(self, force_download: bool = False) -> pd.DataFrame:
        """TBQ01 vessel arrivals (count only, not gross tonnage) for the main ports."""
        df = self.load_table_df("TBQ01", force_download=force_download)
        df = df[df["statistic"] == ARRIVALS]
        major_ports = ["Dublin", "Cork", "Rosslare", "Shannon Foynes", "Waterford", "All Main Irish Ports"]
        return df[df["port"].isin(major_ports)].copy()

    def get_roro_units(self, force_download: bool = False) -> pd.DataFrame:
        """TBQ03 loaded and empty Ro-Ro freight vehicles/trailers (counts) by port and direction."""
        df = self.load_table_df("TBQ03", force_download=force_download)
        df = df[df["statistic"].isin([RORO_LOADED_UNITS, RORO_EMPTY_UNITS])]
        return df[df["port"].isin(STUDY_PORTS + ["All Main Irish Ports"])].copy()

    def get_lolo_container_units(self, force_download: bool = False) -> pd.DataFrame:
        """TBQ04 Lo-Lo container units (count). This is container traffic, not Ro-Ro."""
        df = self.load_table_df("TBQ04", force_download=force_download)
        df = df[df["statistic"] == LOLO_TOTAL_UNITS]
        return df[df["port"].isin(["Dublin", "Cork", "Waterford", "Shannon Foynes", "All Main Irish Ports"])].copy()

    def get_roro_freight_units(self, force_download: bool = False) -> pd.DataFrame:
        """Deprecated alias kept for the Week 1 notebook. TBQ04 is Lo-Lo, not Ro-Ro; use get_roro_units()."""
        logger.warning("get_roro_freight_units() is deprecated: TBQ04 is Lo-Lo container traffic. Use get_roro_units().")
        return self.get_lolo_container_units(force_download=force_download)

    def get_trade_region_tonnage(self, force_download: bool = False) -> pd.DataFrame:
        """Goods handled by port and region of trade: TBQ05 for 2017 to 2019, TBQ07 from 2020."""
        old = self.load_table_df("TBQ05", force_download=force_download)
        new = self.load_table_df("TBQ07", force_download=force_download)
        old = old[(old["statistic_label"] == "Goods Handled") & (old["year"] < 2020)]
        new = new[new["statistic_label"] == "Goods Handled"]
        cols = ["year", "quarter", "quarter_num", "port", "region_of_trade", "value"]
        both = pd.concat([old[cols], new[cols]], ignore_index=True)
        return both[both["port"].isin(STUDY_PORTS + ["All Main Irish Ports"])].copy()

    # ------------------------------------------------------------------ combined matrix
    def build_port_activity_matrix(self) -> pd.DataFrame:
        """
        Quarterly matrix for Dublin, Rosslare and Cork: vessel arrivals, loaded and empty Ro-Ro
        units (all directions and inward), GB and EU goods tonnage, and the GB share of GB plus EU trade.
        """
        keys = ["year", "quarter", "quarter_num", "port"]
        arrivals = self.get_port_arrivals()
        arr = arrivals[arrivals["port"].isin(STUDY_PORTS)].groupby(keys)["value"].sum().rename("vessel_arrivals")

        roro = self.get_roro_units()
        roro = roro[roro["port"].isin(STUDY_PORTS)]
        loaded_all = (roro[(roro["statistic"] == RORO_LOADED_UNITS) & (roro["direction"] == "All directions")]
                      .groupby(keys)["value"].sum().rename("roro_loaded_units"))
        loaded_in = (roro[(roro["statistic"] == RORO_LOADED_UNITS) & (roro["direction"] == "Inward")]
                     .groupby(keys)["value"].sum().rename("roro_loaded_inward"))
        empty_all = (roro[(roro["statistic"] == RORO_EMPTY_UNITS) & (roro["direction"] == "All directions")]
                     .groupby(keys)["value"].sum().rename("roro_empty_units"))

        trade = self.get_trade_region_tonnage()
        trade = trade[trade["port"].isin(STUDY_PORTS)]
        gb = trade[trade["region_of_trade"].isin(GB_REGION_LABELS)].groupby(keys)["value"].sum().rename("gb_tonnes_000")
        eu = trade[trade["region_of_trade"].isin(EU_REGION_LABELS)].groupby(keys)["value"].sum().rename("eu_tonnes_000")

        m = pd.concat([arr, loaded_all, loaded_in, empty_all, gb, eu], axis=1).reset_index()
        m = m.sort_values(["port", "year", "quarter_num"]).reset_index(drop=True)
        m["roro_units_per_arrival"] = (m["roro_loaded_units"] / m["vessel_arrivals"].replace(0, float("nan"))).round(1)
        denom = (m["gb_tonnes_000"] + m["eu_tonnes_000"]).replace(0, float("nan"))
        m["gb_share"] = (m["gb_tonnes_000"] / denom).round(3)
        return m
