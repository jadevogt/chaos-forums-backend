from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, nullable=False)


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)
    password: str


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    password: str = Field(nullable=False)
    server_wide_password: str = Field(nullable=False)


class UserUpdate(UserBase):
    username: str | None = None
    password: str | None = None


class UserLogin(UserBase):
    password: str
