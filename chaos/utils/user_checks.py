from fastapi import HTTPException
from sqlmodel import Session

from chaos.models.user import User


def get_user_or_404(user_id: int, session: Session) -> User:
    user_db: User | None = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="Profile not found")
    return user_db
