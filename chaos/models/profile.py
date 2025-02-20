from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class ProfileBase(SQLModel):
    name: str = Field(index=True, unique=True, nullable=False)
    bio: str | None = Field(nullable=True)
    image: str | None = Field(nullable=True)
    signature: str | None = Field(nullable=True)


class Profile(ProfileBase, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)
    ownership_hash: str | None = Field(default=None)
    is_moderator: bool = Field(default=False)


class ProfilePublic(ProfileBase):
    id: int
    is_moderator: bool


class ProfileCreate(ProfileBase):
    bio: str | None = None
    image: str | None = None
    signature: str | None = None


class ProfileUpdate(ProfileBase):
    name: str | None = None
    bio: str | None = None
    image: str | None = None
    signature: str | None = None


class ProfileModeratorUpdate(BaseModel):
    """
    Used when a "moderator" promotes or demotes another user
    """

    actor_id: int
    is_moderator: bool | None = None
