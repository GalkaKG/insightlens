"""Facade package for ingestion utilities.

Re-exports functions from `app.api.data_ingest` so callers can import
from `app.ingestion` for clearer project organization.
"""
from app.api.data_ingest import read_table, ParsingError, MaxRowsExceededError, IngestionError

__all__ = ["read_table", "ParsingError", "MaxRowsExceededError", "IngestionError"]
