"""Testes de integração da API (/solve, /export)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

PAYLOAD = {
    "alternatives": ["A", "B", "C"],
    "criteria": [
        {"name": "Custo", "weight": 0.6, "maximize": False, "preference": "usual"},
        {"name": "Qualidade", "weight": 0.4, "maximize": True, "preference": "v_shape", "p": 5.0},
    ],
    "matrix": [
        [250.0, 16.0],
        [200.0, 24.0],
        [300.0, 20.0],
    ],
}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_solve_returns_ranking_and_gaia():
    resp = client.post("/api/solve", json=PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["scores"]) == 3
    ranks = sorted(s["rank"] for s in data["scores"])
    assert ranks == [1, 2, 3]
    assert data["gaia"] is not None
    assert 0.0 <= data["gaia"]["quality"] <= 1.0


def test_solve_validation_error():
    bad = {**PAYLOAD, "matrix": [[1.0]]}  # dimensões inconsistentes
    assert client.post("/api/solve", json=bad).status_code == 422


def test_export_csv():
    resp = client.post("/api/export/csv", json=PAYLOAD)
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert b"Rank" in resp.content


def test_export_pdf():
    resp = client.post("/api/export/pdf", json=PAYLOAD)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"
