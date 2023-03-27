from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    reload: bool = False

    postgres_host: str = "0.0.0.0"
    postgres_port: int = 5432
    postgres_user: str
    postgres_password: str
    postgres_db: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30


settings = Settings(
    _env_file=".env",
    _env_file_encoding="UTF-8"
)
