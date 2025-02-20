from typing import Sequence, Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from chaos.dependencies import SessionDep
from chaos.models.profile import (
    ProfilePublic,
    Profile,
    ProfileUpdate,
    ProfileCreate,
    ProfileModeratorUpdate,
)
from chaos.utils.authentication import UserDep
from utils.authentication import generate_ownership_hash
from utils.profile_checks import (
    get_profile_or_404,
    check_user_and_profile_moderator,
    get_profile_and_check_ownership,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=ProfilePublic)
def create_profile(profile: ProfileCreate, session: SessionDep, current_user: UserDep):
    db_profile = Profile.model_validate(profile)
    db_profile.ownership_hash = generate_ownership_hash(current_user.id, db_profile.id)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.get("/", response_model=Sequence[ProfilePublic])
def read_profiles(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    profiles = session.exec(select(Profile).offset(offset).limit(limit)).all()
    return profiles


@router.get("/{profile_id}", response_model=ProfilePublic)
def read_profile(profile_id: int, session: SessionDep):
    return get_profile_or_404(profile_id, session)


@router.patch("/{profile_id}", response_model=ProfilePublic)
def update_user(
    profile_id: int, profile: ProfileUpdate, session: SessionDep, current_user: UserDep
):
    profile_db = get_profile_and_check_ownership(profile_id, session, current_user)
    profile_data = profile.model_dump(exclude_unset=True)
    profile_db.sqlmodel_update(profile_data)
    session.add(profile_db)
    session.commit()
    session.refresh(profile_db)
    return profile_db


@router.delete("/{profile_id}")
def delete_user(profile_id: int, session: SessionDep, current_user: UserDep):
    profile_db = get_profile_and_check_ownership(profile_id, session, current_user)
    session.delete(profile_db)
    session.commit()
    return {"ok": True}


@router.post("/{profile_id}/promote", response_model=ProfilePublic)
def promote_user(
    profile_id: int,
    profile_moderator_update: ProfileModeratorUpdate,
    session: SessionDep,
    current_user: UserDep,
):
    target_profile = get_profile_or_404(profile_id, session)
    actor_profile = get_profile_or_404(profile_moderator_update.actor_id, session)
    check_user_and_profile_moderator(actor_profile, current_user)
    target_profile.is_moderator = profile_moderator_update.is_moderator
    session.add(target_profile)
    session.commit()
    session.refresh(target_profile)
    return target_profile
