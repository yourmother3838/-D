from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Helpdesk"
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    jwt_algorithm: str = "HS256"
    cors_origin: str = "http://localhost:3000"
    redis_url: str = "redis://localhost:6379/0"
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()