"""
Data ingestion and preprocessing module for IrishLogix.
"""

from .cso_loader import CSODataLoader, CSO_TABLES

__all__ = ["CSODataLoader", "CSO_TABLES"]
