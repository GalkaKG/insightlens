import pandas as pd

from app.api.validation import (
    missingness_validator,
    type_consistency_validator,
    duplicate_detector,
    iqr_outlier_detector,
)


def test_missingness_validator():
    df = pd.DataFrame({"a": [1, None, 3], "b": [None, None, None]})
    res = missingness_validator(df, threshold=0.66)
    assert res["rule"] == "missingness"
    assert "b" in res["flags"] and "a" not in res["flags"]


def test_type_consistency_validator():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [1, "x", 3]})
    res = type_consistency_validator(df)
    assert res["rule"] == "type_consistency"
    assert "b" in res["issues"] and "a" not in res["issues"]


def test_duplicate_detector():
    df = pd.DataFrame({"x": [1, 1, 2], "y": ["a", "a", "b"]})
    res = duplicate_detector(df)
    assert res["rule"] == "duplicates"
    assert res["duplicate_count"] >= 2


def test_iqr_outlier_detector():
    df = pd.DataFrame({"v": [1, 2, 3, 100]})
    res = iqr_outlier_detector(df, multiplier=1.5)
    assert res["rule"] == "iqr_outliers"
    assert res["columns"].get("v", 0) >= 1
