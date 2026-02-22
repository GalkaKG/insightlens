"""Facade package for validation utilities.

Re-exports from `app.api.validation` for clearer public API.
"""
from app.api.validation import (
    missingness_validator,
    type_consistency_validator,
    duplicate_detector,
    iqr_outlier_detector,
    load_config,
)

__all__ = [
    "missingness_validator",
    "type_consistency_validator",
    "duplicate_detector",
    "iqr_outlier_detector",
    "load_config",
]
