import pandas as pd
from pathlib import Path

from app.api.data_ingest import read_table
from main import _analyze_dataframe


def test_read_csv(tmp_path: Path):
    p = tmp_path / "sample.csv"
    p.write_text("id,value\n1,10\n2,20\n3,\n")
    df = read_table(p)
    assert df.shape == (3, 2)


def test_analyze_dataframe_basic():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [1.0, None, 3.0, 4.0]})
    res = _analyze_dataframe(df, missingness_threshold=0.5)
    assert res["n_rows"] == 4
    assert res["n_columns"] == 2
    assert isinstance(res["descriptive_stats"], dict)