from random import randint

from sqlmodel import Session
from starlette.testclient import TestClient

from chaos.models.profile import Profile
from chaos.models.user import User
from utils.authentication import generate_ownership_hash


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


def test_get_user_profiles(
    client: TestClient,
    user_instance: User,
    profile_instance: Profile,
    access_token_instance: str,
    alt_access_token_instance: str,
    alt_user_instance: User,
    example_profile_payload: dict,
    session: Session,
):
    # create a bunch of alternate user profiles
    for i in range(10):
        args = {**example_profile_payload, "name": str(randint(0, 9999))}
        profile = Profile(**args)
        session.add(profile)
        session.commit()
        session.refresh(profile)
        profile.ownership_hash = generate_ownership_hash(
            alt_user_instance.id, profile.id
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
    response = client.get(
        f"/users/{user_instance.id}/profiles/",
        headers={"Authorization": f"Bearer {access_token_instance}"},
    )
    print(profile_instance.ownership_hash)
    assert 199 < response.status_code < 300
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == profile_instance.name
