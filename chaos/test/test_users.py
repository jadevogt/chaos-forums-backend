from fastapi.testclient import TestClient
from chaos.config import settings
from chaos.models.user import User


def test_create_user(client: TestClient, example_credentials: dict):
    payload = {
        **example_credentials,
        "server_wide_password": settings.server_wide_password,
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["username"] == "test"
    assert "id" in response_data


def test_user_login(client: TestClient, user_instance: User, example_credentials: dict):
    response = client.post(
        "/login/",
        json={
            "username": example_credentials["username"],
            "password": example_credentials["password"],
        },
    )
    assert response.status_code == 200


def test_delete_user(
    client: TestClient, user_instance: User, access_token_instance: str
):
    response = client.delete(
        f"/users/{user_instance.id}",
        headers={"Authorization": f"Bearer {access_token_instance}"},
    )
    assert 199 < response.status_code < 300
    assert response.json()["ok"]


def test_user_duplicate_username(
    client: TestClient, example_credentials: dict, user_instance: User
):
    payload = {
        **example_credentials,
        "server_wide_password": settings.server_wide_password,
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 400
