from starlette.testclient import TestClient

from chaos.models.profile import Profile


def test_create_profile(
    client: TestClient,
    user_instance: dict,
    access_token_instance: str,
    example_profile_payload: dict,
):
    response = client.post(
        "/profiles/",
        json=example_profile_payload,
        headers={"Authorization": f"Bearer {access_token_instance}"},
    )
    assert 199 < response.status_code < 300
    assert response.json()["name"] == example_profile_payload["name"]
    assert response.json()["bio"] == example_profile_payload["bio"]
    assert response.json()["image"] == example_profile_payload["image"]
    assert response.json()["signature"] == example_profile_payload["signature"]


def test_delete_profile(
    client: TestClient, profile_instance: Profile, access_token_instance: str
):
    response = client.delete(
        f"/profiles/{profile_instance.id}",
        headers={"Authorization": f"Bearer {access_token_instance}"},
    )
    assert 199 < response.status_code < 300
    assert response.json()["ok"]


def test_delete_profile_unauthorized(
    client: TestClient, profile_instance: Profile, alt_access_token_instance: str
):
    response = client.delete(
        f"/profiles/{profile_instance.id}",
        headers={"Authorization": f"Bearer {alt_access_token_instance}"},
    )
    assert response.status_code == 403


def test_update_profile(
    client: TestClient,
    profile_instance: Profile,
    access_token_instance: str,
    example_profile_payload: dict,
):
    payload = {"signature": "made a change (:"}
    response = client.patch(
        f"/profiles/{profile_instance.id}",
        json=payload,
        headers={"Authorization": f"Bearer {access_token_instance}"},
    )
    assert 199 < response.status_code < 300
    assert profile_instance.signature == payload["signature"]


def test_update_profile_unauthorized(
    client: TestClient,
    profile_instance: Profile,
    alt_access_token_instance: str,
    example_profile_payload: dict,
):
    payload = {"signature": "made a change (evil) (:<"}
    response = client.patch(
        f"/profiles/{profile_instance.id}",
        json=payload,
        headers={"Authorization": f"Bearer {alt_access_token_instance}"},
    )
    assert response.status_code == 403
