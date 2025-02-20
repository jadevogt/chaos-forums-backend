import warnings

import pytest
from sqlalchemy.exc import SAWarning
from sqlmodel import Session
from starlette.testclient import TestClient

from chaos.models.user import User
from chaos.models.profile import Profile
from chaos.utils.authentication import hash_password, create_access_token
from utils.authentication import generate_ownership_hash


@pytest.fixture(name="user_instance")
def user_instance_fixture(
    client: TestClient, session: Session, example_credentials: dict
):
    user = User(
        username=example_credentials["username"],
        password=example_credentials["password"],
    )
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user
    with warnings.catch_warnings():
        # Don't show warnings if the row has already been deleted by test
        warnings.filterwarnings("ignore", category=SAWarning)
        session.delete(user)
        session.commit()


@pytest.fixture(name="alt_user_instance")
def alt_user_instance_fixture(
    client: TestClient, session: Session, alt_example_credentials: dict
):
    user = User(
        username=alt_example_credentials["username"],
        password=alt_example_credentials["password"],
    )
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    yield user
    with warnings.catch_warnings():
        # Don't show warnings if the row has already been deleted by test
        warnings.filterwarnings("ignore", category=SAWarning)
        session.delete(user)
        session.commit()


@pytest.fixture(name="access_token_instance")
def access_token_instance_fixture(
    client: TestClient, user_instance: User, example_credentials: dict
):
    token = create_access_token(data={"user_id": user_instance.id})
    yield token


@pytest.fixture(name="alt_access_token_instance")
def alt_access_token_instance_fixture(
    client: TestClient, alt_user_instance: User, example_credentials: dict
):
    token = create_access_token(data={"user_id": alt_user_instance.id})
    yield token


@pytest.fixture(name="profile_instance")
def profile_instance_fixture(
    client: TestClient,
    user_instance: User,
    example_profile_payload: dict,
    session: Session,
):
    profile = Profile(**example_profile_payload)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    profile.ownership_hash = generate_ownership_hash(user_instance.id, profile.id)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    yield profile
    with warnings.catch_warnings():
        # Don't show warnings if the row has already been deleted by test
        warnings.filterwarnings("ignore", category=SAWarning)
        session.delete(profile)
        session.commit()
