from typing import Sequence, Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select

from dependencies import SessionDep
from models.profile import ProfilePublic, Profile, ProfileUpdate, ProfileCreate
from utils import UserDep

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.post("/", response_model=ProfilePublic)
def create_profile(profile: ProfileCreate, session: SessionDep, current_user: UserDep):
    db_profile = Profile.model_validate(profile)
    db_profile.user = current_user.id
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile


@router.get("/", response_model=Sequence[ProfilePublic])
def read_profiles(
        session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    profiles = session.exec(select(Profile).offset(offset).limit(limit)).all()
    return profiles


@router.get("/{profile_id}", response_model=ProfilePublic)
def read_profile(profile_id: int, session: SessionDep):
    profile_db = session.get(Profile, profile_id)
    if not profile_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile_db


@router.patch("/{profile_id}", response_model=ProfilePublic)
def update_user(
        profile_id: int, profile: ProfileUpdate, session: SessionDep, current_user: UserDep
):
    profile_db = session.get(Profile, profile_id)
    if not profile_db:
        raise HTTPException(status_code=404, detail="User not found")
    if not profile_db.user == current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    profile_data = profile.model_dump(exclude_unset=True)
    profile_db.sqlmodel_update(profile_data)
    session.add(profile_db)
    session.commit()
    session.refresh(profile_db)
    return profile_db


@router.delete("/{profile_id}")
def delete_user(profile_id: int, session: SessionDep, current_user: UserDep):
    profile_db = session.get(Profile, profile_id)
    if not profile_db:
        raise HTTPException(status_code=404, detail="User not found")
    if not profile_db.user == current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    session.delete(profile_db)
    session.commit()
    return {"ok": True}
