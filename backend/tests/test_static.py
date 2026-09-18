"""Serving the built frontend as a single-page app."""

from pathlib import Path

from fastapi.testclient import TestClient

from acoustic_dashboard.config import Settings
from acoustic_dashboard.main import create_app


def make_client(static_dir: Path) -> TestClient:
    return TestClient(create_app(Settings(static_dir=static_dir)))


def test_no_build_dir_means_no_spa(tmp_path: Path):
    client = make_client(tmp_path / "missing")

    assert client.get("/api/health").status_code == 200
    assert client.get("/").status_code == 404


def test_serves_index_and_assets(tmp_path: Path):
    (tmp_path / "index.html").write_text("<h1>app</h1>")
    (tmp_path / "_app").mkdir()
    (tmp_path / "_app" / "chunk.js").write_text("console.log(1)")
    client = make_client(tmp_path)

    assert client.get("/").text == "<h1>app</h1>"
    assert client.get("/_app/chunk.js").text == "console.log(1)"


def test_client_routes_fall_back_to_index(tmp_path: Path):
    (tmp_path / "index.html").write_text("<h1>app</h1>")
    client = make_client(tmp_path)

    response = client.get("/machines/m1")

    assert response.status_code == 200
    assert response.text == "<h1>app</h1>"


def test_api_is_not_shadowed(tmp_path: Path):
    (tmp_path / "index.html").write_text("<h1>app</h1>")
    client = make_client(tmp_path)

    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/nope").status_code == 404


def test_path_traversal_is_refused(tmp_path: Path):
    (tmp_path / "index.html").write_text("<h1>app</h1>")
    (tmp_path.parent / "secret.txt").write_text("nope")
    client = make_client(tmp_path)

    response = client.get("/../secret.txt")

    assert "nope" not in response.text
