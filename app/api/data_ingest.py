"""Data ingestion helpers for InsightLens.

This module provides utilities to read CSV and single-sheet Excel files into
pandas DataFrames with consistent normalization for student projects:

- normalize column names to snake_case
- trim whitespace in string columns
- standardize common missing-value encodings to pandas NA
- enforce a maximum row limit to avoid over-consuming memory on a laptop

The functions raise descriptive exceptions on parsing errors to aid debugging
and testing.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List, Optional, Union

import pandas as pd


class IngestionError(Exception):
    """Base exception for ingestion-related errors."""


class ParsingError(IngestionError):
    """Raised when a file cannot be parsed as CSV or Excel."""


class MaxRowsExceededError(IngestionError):
    """Raised when a file exceeds the configured maximum number of rows."""


def _to_snake_case(name: str) -> str:
    """Convert an arbitrary column name to snake_case.

    This is intentionally conservative: non-alphanumeric characters are
    replaced with underscores, consecutive underscores are collapsed, and the
    result is lowercased.
    """
    if not isinstance(name, str):
        name = str(name)
    # Replace non-alphanumeric characters with underscore
    s = re.sub(r"[^0-9a-zA-Z]+", "_", name)
    # Insert underscore before camelCase transitions (e.g., 'StartDate' -> 'Start_Date')
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.strip("_")
    s = re.sub(r"__+", "_", s)
    return s.lower()


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of `df` with column names converted to snake_case.

    The function returns a new DataFrame reference (it does not modify the
    original in-place) to make transformations explicit in calling code.
    """
    mapping = {col: _to_snake_case(col) for col in df.columns}
    return df.rename(columns=mapping)


def trim_whitespace(df: pd.DataFrame, inplace: bool = False) -> pd.DataFrame:
    """Trim leading/trailing whitespace from string-like columns.

    Parameters
    - df: DataFrame to operate on
    - inplace: when True modify `df` in place and return it, otherwise
      return a new DataFrame copy.
    """
    target = df if inplace else df.copy()
    # Select object and string dtypes
    string_cols = target.select_dtypes(include=["object", "string"]).columns
    for col in string_cols:
        # Use .astype(object) to avoid pandas string-dtype surprises
        target[col] = target[col].astype(object).map(lambda v: v.strip() if isinstance(v, str) else v)
    return target


def standardize_missing_values(df: pd.DataFrame, extra_na: Optional[Iterable[str]] = None, inplace: bool = False) -> pd.DataFrame:
    """Standardize common textual missing-value encodings to pandas NA.

    The replacement is applied to object/string columns to avoid coercing
    numeric columns unexpectedly.
    """
    if extra_na is None:
        extra_na = ["NA", "N/A", "na", "n/a", "None", "NULL", "null", "\\N", ""]
    # Normalize to lowercase for matching
    lower_set = {s.lower() for s in extra_na}

    target = df if inplace else df.copy()
    for col in target.select_dtypes(include=["object", "string"]).columns:
        # Replace exact string matches (case-insensitive) with pd.NA
        series = target[col]
        # Only operate on non-null values
        mask = series.notna() & series.astype(str).str.lower().isin(lower_set)
        if mask.any():
            target.loc[mask, col] = pd.NA
    return target


def read_table(path: Union[str, Path], max_rows: int = 100_000, sheet_name: Optional[Union[int, str]] = 0) -> pd.DataFrame:
    """Read a CSV or single-sheet Excel file and apply normalization.

    Parameters
    - path: path to the CSV or Excel file
    - max_rows: maximum allowed rows (inclusive). Files with more rows raise
      `MaxRowsExceededError`.
    - sheet_name: sheet name or index for Excel files (default: first sheet)

    Returns a normalized pandas DataFrame.

    Raises
    - ParsingError: if pandas fails to parse the file
    - MaxRowsExceededError: if the file contains more than `max_rows` rows
    """
    p = Path(path)
    if not p.exists():
        raise ParsingError(f"File does not exist: {p}")

    suffix = p.suffix.lower()
    try:
        if suffix in {".xls", ".xlsx"}:
            # Read up to max_rows+1 to check size without loading huge files
            df = pd.read_excel(p, sheet_name=sheet_name, nrows=max_rows + 1)
        elif suffix in {".csv", ""}:
            df = pd.read_csv(p, nrows=max_rows + 1)
        else:
            raise ParsingError(f"Unsupported file extension: {suffix}")
    except Exception as exc:
        raise ParsingError(f"Failed to parse {p.name}: {exc}") from exc

    if df.shape[0] > max_rows:
        raise MaxRowsExceededError(f"File {p.name} has {df.shape[0]} rows which exceeds limit {max_rows}")

    # Apply deterministic normalization steps
    df = normalize_column_names(df)
    df = trim_whitespace(df, inplace=False)
    df = standardize_missing_values(df, inplace=False)

    return df


__all__ = [
    "read_table",
    "normalize_column_names",
    "trim_whitespace",
    "standardize_missing_values",
    "ParsingError",
    "MaxRowsExceededError",
    "IngestionError",
]


if __name__ == "__main__":
    # Example usage for local experimentation
    example = Path(__file__).parent.parent / "examples" / "sample.csv"
    print(f"Reading example file: {example}")
    try:
        df = read_table(example)
        print(df.head())
        print(df.dtypes)
    except IngestionError as e:
        print(f"Failed to ingest sample file: {e}")
