from sqlmodel import SQLModel, Field

class ProfileBase(SQLModel):
    name: str = Field(index=True, unique=True, nullable=False)
    bio: str | None = Field(nullable=True)
    image: str | None = Field(nullable=True)
    signature: str | None = Field(nullable=True)


class Profile(ProfileBase, table=True):
    id: int = Field(default=None, primary_key=True, unique=True)
    user: int | None = Field(default=None, foreign_key="user.id")


class ProfilePublic(ProfileBase):
    id: int


class ProfileCreate(ProfileBase):
    bio: str | None = None
    image: str | None = None
    signature: str | None = None


class ProfileUpdate(ProfileBase):
    name: str | None = None
    bio: str | None = None
    image: str | None = None
    signature: str | None = None