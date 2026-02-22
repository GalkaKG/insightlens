from fastapi.testclient import TestClient

from main import app


def test_status_endpoint():
    client = TestClient(app)
    r = client.get("/status")
    assert r.status_code == 200
    assert "OK" in r.text


def test_upload_and_analyze_roundtrip():
    client = TestClient(app)
    csv_bytes = b"id,value\n1,10\n2,20\n"
    files = {"file": ("sample.csv", csv_bytes, "text/csv")}
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    data = r.json()
    upload_id = data["upload_id"]

    # Trigger analysis
    r2 = client.post("/analyze", json={"upload_id": upload_id})
    assert r2.status_code == 200
    body = r2.json()
    report_id = body["report_id"]

    # Retrieve report as html and json
    r3 = client.get(f"/report/{report_id}?format=html")
    assert r3.status_code == 200
    assert "InsightLens Report" in r3.text
    r4 = client.get(f"/report/{report_id}?format=json")
    assert r4.status_code == 200
    assert "n_rows" in r4.json()
