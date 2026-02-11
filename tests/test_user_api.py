from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


client = TestClient(app)


def _headers() -> dict[str, str]:
    settings = get_settings()
    return {settings.api_key_header: settings.active_api_keys[0].get_secret_value(), "X-User-Id": "tester"}


def test_create_and_get_user() -> None:
    payload = {"email": "alice@example.com", "full_name": "Alice Smith", "bio": "<script>x</script>Hello"}
    create = client.post("/users", json=payload, headers=_headers())
    assert create.status_code == 201
    user = create.json()
    assert user["bio"] == "xHello"

    response = client.get(f"/users/{user['id']}", headers=_headers())
    assert response.status_code == 200
    assert response.json()["email"] == payload["email"]


def test_reject_unknown_field() -> None:
    payload = {
        "email": "bob@example.com",
        "full_name": "Bob Jones",
        "bio": "ok",
        "is_admin": True,
    }
    response = client.post("/users", json=payload, headers=_headers())
    assert response.status_code == 422


def test_missing_api_key() -> None:
    response = client.get("/users")
    assert response.status_code == 401
