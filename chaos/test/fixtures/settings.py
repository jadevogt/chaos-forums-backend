import pytest


@pytest.fixture(name="example_credentials")
def example_credentials_fixture():
    yield {
        "username": "test",
        "password": "password",
    }


@pytest.fixture(name="alt_example_credentials")
def alt_example_credentials_fixture():
    yield {
        "username": "othertest",
        "password": "otherpassword",
    }


@pytest.fixture(name="example_profile_payload")
def example_profile_payload_fixture():
    yield {
        "name": "test_profile_user",
        "bio": "test_profile_bio",
        "image": "test_profile_image",
        "signature": "trying to make a change :/",
    }
