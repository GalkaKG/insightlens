"""Validation engine for InsightLens.

Provides a small set of rule-based validators that operate on pandas DataFrames
and return JSON-serializable summaries. Each validator is deterministic and
configured via a simple thresholds dict which can be loaded from JSON.
"""

from __future__ import annotations

from typing import Dict, Any

import json
import pandas as pd


def load_config(path: str) -> Dict[str, Any]:
    """Load validator configuration from a JSON file.

    The config is a plain mapping of validator names to threshold values.
    """
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def missingness_validator(df: pd.DataFrame, threshold: float = 0.5) -> Dict[str, Any]:
    """Identify columns whose missing fraction meets or exceeds `threshold`.

    Returns a dict: {"rule": "missingness", "threshold": float, "flags": {col: frac}}
    """
    n = df.shape[0]
    if n == 0:
        return {"rule": "missingness", "threshold": threshold, "flags": {}}
    missing = df.isna().sum()
    frac = (missing / n).to_dict()
    flags = {col: float(fr) for col, fr in frac.items() if fr >= threshold}
    return {"rule": "missingness", "threshold": float(threshold), "flags": flags}


def type_consistency_validator(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect columns that contain mixed types inconsistent with the majority type.

    Returns: {"rule": "type_consistency", "issues": {col: {"types": {repr:type_count}}}}
    """
    issues = {}
    for col in df.columns:
        series = df[col].dropna()
        type_counts: Dict[str, int] = {}
        for v in series:
            t = type(v).__name__
            type_counts[t] = type_counts.get(t, 0) + 1
        if not type_counts:
            continue
        if len(type_counts) > 1:
            issues[col] = {"types": type_counts}
    return {"rule": "type_consistency", "issues": issues}


def duplicate_detector(df: pd.DataFrame) -> Dict[str, Any]:
    """Return duplicate row counts and sample duplicated indices.

    Returns: {"rule": "duplicates", "duplicate_count": int, "sample_indices": [int,...]}
    """
    dup_mask = df.duplicated(keep=False)
    dup_count = int(dup_mask.sum())
    sample = []
    if dup_count > 0:
        sample = [int(i) for i in df[dup_mask].index.tolist()[:10]]
    return {"rule": "duplicates", "duplicate_count": dup_count, "sample_indices": sample}


def iqr_outlier_detector(df: pd.DataFrame, multiplier: float = 1.5) -> Dict[str, Any]:
    """Compute IQR-based outlier counts for numeric columns.

    Returns: {"rule": "iqr_outliers", "multiplier": float, "columns": {col: outlier_count}}
    """
    result: Dict[str, Any] = {"rule": "iqr_outliers", "multiplier": float(multiplier), "columns": {}}
    numeric = df.select_dtypes(include=["number"]).columns
    for col in numeric:
        series = df[col].dropna()
        if series.empty:
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - multiplier * iqr
        upper = q3 + multiplier * iqr
        n_out = int(((series < lower) | (series > upper)).sum())
        result["columns"][col] = int(n_out)
    return result


__all__ = [
    "load_config",
    "missingness_validator",
    "type_consistency_validator",
    "duplicate_detector",
    "iqr_outlier_detector",
]
