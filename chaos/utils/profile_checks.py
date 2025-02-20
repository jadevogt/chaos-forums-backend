from fastapi import HTTPException
from sqlmodel import Session

from chaos.models.profile import Profile
from chaos.models.user import User
from utils.authentication import generate_ownership_hash


def get_profile_or_404(profile_id: int, session: Session) -> Profile:
    profile_db: Profile | None = session.get(Profile, profile_id)
    if not profile_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_db


def check_user_profile_ownership(profile: Profile, user: User):
    """
    Throw 403 if the user is not the owner of the profile
    """
    expected_hash = generate_ownership_hash(user.id, profile.id)
    if profile.ownership_hash != expected_hash:
        raise HTTPException(status_code=403, detail="Not allowed")


def get_profile_and_check_ownership(profile_id: int, session: Session, user: User):
    profile = get_profile_or_404(profile_id, session)
    check_user_profile_ownership(profile, user)
    return profile


def check_profile_moderator(profile: Profile) -> None:
    """
    Throw 403 if the profile is not a moderator
    """
    if not profile.is_moderator:
        raise HTTPException(status_code=403, detail="Not allowed")


def check_user_and_profile_moderator(profile: Profile, user: User):
    """
    Convenience function to check both the user and profile ownership and moderator status
    """
    check_user_profile_ownership(profile, user)
    check_profile_moderator(profile)
