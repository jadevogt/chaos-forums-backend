from fastapi import APIRouter, HTTPException

from dependencies import SessionDep
from models.token import Token
from models.user import UserLogin, User
from utils import verify_password, create_access_token

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, session: SessionDep):
    db_user = (
        session.query(User).filter(User.username == user_credentials.username).first()
    )
    print(db_user)
    print(user_credentials)
    if not db_user:
        raise HTTPException(status_code=404, detail="Invalid credentials")
    if not verify_password(user_credentials.password, db_user.password):
        raise HTTPException(status_code=404, detail="Invalid credentials")
    access_token = create_access_token(data={"user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}
