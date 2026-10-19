from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)

ALLOWED_ORIGIN = settings.cors_origins_list[0]


def preflight(origin: str):
    return client.options(
        "/api/v1/sections/",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )


def test_preflight_allows_configured_origin():
    response = preflight(ALLOWED_ORIGIN)

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


def test_preflight_rejects_unknown_origin():
    response = preflight("http://evil.example")

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_simple_request_gets_cors_header():
    response = client.get("/docs", headers={"Origin": ALLOWED_ORIGIN})

    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
