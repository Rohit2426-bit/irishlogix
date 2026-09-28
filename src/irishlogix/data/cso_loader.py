"""
Automated Data Loader and Preprocessor for Irish Central Statistics Office (CSO)
Maritime and Port Traffic Datasets.

Fetches open data via CSO PxStat REST API and standardizes it for predictive
port congestion modeling (Component 1) and baseline freight routing.
"""

import os
import io
import logging
import urllib.request
import urllib.error
import pandas as pd
from pathlib import Path
from typing import Optional, Dict

logger = logging.getLogger(__name__)

CSO_API_BASE_URL = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset"

# Recognized CSO Maritime Tables
CSO_TABLES = {
    "TBQ01": "Vessel Arrivals by Port and Quarter",
    "TBQ02": "Tonnage of Goods Handled by Cargo Category",
    "TBQ04": "Ro-Ro Freight Unit Traffic by Direction and Port",
    "TBQ05": "Tonnage Handled by Port and Region of Trade (GB & EU)",
}

DEFAULT_CACHE_DIR = Path("data/raw/cso")


class CSODataLoader:
    """Manages downloading, local caching, and parsing of CSO port traffic tables."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_raw_table(self, table_code: str, force_download: bool = False) -> str:
        """
        Retrieves raw CSV string for a given CSO table code, using cache when available.
        """
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
            url,
            headers={
                "User-Agent": "IrishLogix-ResearchPracticum-NCI/1.0 (academic data ingestion)"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                raw_bytes = response.read()
                raw_text = raw_bytes.decode("utf-8-sig")

                # Cache to disk
                with open(cache_file, "w", encoding="utf-8-sig") as f:
                    f.write(raw_text)

                logger.info(f"Successfully cached {len(raw_text)} chars to {cache_file}")
                return raw_text

        except urllib.error.URLError as e:
            logger.error(f"Failed to fetch {table_code} from CSO API: {e}")
            if cache_file.exists():
                logger.info(f"Falling back to stale local cache for {table_code}")
                with open(cache_file, "r", encoding="utf-8-sig") as f:
                    return f.read()
            raise

    def load_table_df(self, table_code: str, force_download: bool = False) -> pd.DataFrame:
        """Downloads/loads table and returns cleaned Pandas DataFrame."""
        raw_text = self.fetch_raw_table(table_code, force_download=force_download)
        df = pd.read_csv(io.StringIO(raw_text))

        # Standardize column headers
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

        # Parse Quarter column into year and quarter number if present
        if "quarter" in df.columns:
            # e.g., '2017Q1' -> year 2017, quarter 1
            df["year"] = df["quarter"].str[:4].astype(int)
            df["quarter_num"] = df["quarter"].str[-1].astype(int)

        # Standardize numeric values
        if "value" in df.columns:
            df["value"] = pd.to_numeric(df["value"].astype(str).str.replace(",", ""), errors="coerce")

        return df

    def get_port_arrivals(self, force_download: bool = False) -> pd.DataFrame:
        """
        Loads TBQ01 (Vessel arrivals by port) and filters for major Irish ports:
        Dublin, Cork, Rosslare, Shannon Foynes, Waterford.
        """
        df = self.load_table_df("TBQ01", force_download=force_download)
        if "port" in df.columns:
            major_ports = ["Dublin", "Cork", "Rosslare", "Shannon Foynes", "Waterford", "All Main Irish Ports"]
            df = df[df["port"].isin(major_ports)].copy()
        return df

    def get_roro_freight_units(self, force_download: bool = False) -> pd.DataFrame:
        """
        Loads TBQ04 (Ro-Ro Freight Units) by port and direction (inward/outward).
        """
        df = self.load_table_df("TBQ04", force_download=force_download)
        if "port" in df.columns:
            major_ports = ["Dublin", "Cork", "Rosslare", "All Main Irish Ports"]
            df = df[df["port"].isin(major_ports)].copy()
        return df

    def get_trade_region_tonnage(self, force_download: bool = False) -> pd.DataFrame:
        """
        Loads TBQ05 (Goods handled by Port & Region of Trade), critical for
        post-Brexit Great Britain vs EU freight shift tracking.
        """
        df = self.load_table_df("TBQ05", force_download=force_download)
        return df

    def build_port_activity_matrix(self) -> pd.DataFrame:
        """
        Merges arrivals and freight units across Dublin, Cork, and Rosslare to
        create a foundational time-series feature matrix for port congestion.
        """
        arrivals = self.get_port_arrivals()
        roro = self.get_roro_freight_units()

        # Aggregate arrivals by port & quarter
        arr_summary = (
            arrivals[arrivals["port"].isin(["Dublin", "Cork", "Rosslare"])]
            .groupby(["year", "quarter", "quarter_num", "port"])["value"]
            .sum()
            .reset_index()
            .rename(columns={"value": "vessel_arrivals"})
        )

        # Aggregate Ro-Ro freight units (all directions)
        roro_summary = (
            roro[
                (roro["port"].isin(["Dublin", "Cork", "Rosslare"]))
                & (roro["direction"] == "All directions")
            ]
            .groupby(["year", "quarter", "port"])["value"]
            .sum()
            .reset_index()
            .rename(columns={"value": "roro_freight_units"})
        )

        merged = pd.merge(
            arr_summary,
            roro_summary,
            on=["year", "quarter", "port"],
            how="outer"
        ).sort_values(by=["port", "year", "quarter_num"])

        # Calculate unit-to-arrival density metric
        merged["freight_units_per_vessel"] = (
            merged["roro_freight_units"] / merged["vessel_arrivals"].replace(0, float("nan"))
        ).round(1)

        return merged
