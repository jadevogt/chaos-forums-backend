from fastapi import FastAPI
from sqlmodel import Field, SQLModel
from dependencies import create_db_and_tables
from routers.user import router as user_router
from routers.auth import router as auth_router
from routers.profile import router as profile_router

app = FastAPI()
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(profile_router)


class Post(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
