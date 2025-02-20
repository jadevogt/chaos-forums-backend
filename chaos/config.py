from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int
    server_wide_password: str
    algorithm: str = "HS256"
    database_file_name: str = "database.db"


settings = Settings()
