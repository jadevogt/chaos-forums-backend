from typing import Sequence, Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from chaos.config import Settings
from chaos.dependencies import SessionDep
from chaos.models.user import UserCreate, UserPublic, User, UserUpdate
from chaos.utils.authentication import hash_password, UserDep
from chaos.models.profile import Profile
from utils.authentication import generate_ownership_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    user.password = hash_password(user.password)
    if not user.server_wide_password == Settings().server_wide_password:
        raise HTTPException(status_code=403, detail="Not allowed")
    try:
        db_user = User.model_validate(user)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=Sequence[UserPublic])
def read_users(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserPublic)
def read_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int, user: UserUpdate, session: SessionDep, current_user: UserDep
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    if user.password is not None:
        user.password = hash_password(user.password)
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/{user_id}")
def delete_user(user_id: int, session: SessionDep, current_user: UserDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.get("/{user_id}/profiles", response_model=Sequence[Profile])
def get_user_profiles(user_id: int, session: SessionDep, current_user: UserDep):
    if not current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    profiles = session.exec(select(Profile)).all()
    return [
        p
        for p in profiles
        if p.ownership_hash == generate_ownership_hash(user_id, p.id)
    ]
