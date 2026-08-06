"""API endpoint tests."""

from fastapi.testclient import TestClient

from acoustic_dashboard import __version__
from acoustic_dashboard.main import app

client = TestClient(app)


def test_health_check_passes():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}
