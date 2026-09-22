from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  app_name: str = "TurfMatch API"
  api_v1_prefix: str = "/api/v1"
  database_url: str = "postgresql+psycopg://turfmatch:turfmatch@localhost:5432/turfmatch"
  auth_secret: str = "local-development-secret-change-before-production"
  token_expiry_days: int = 7

  model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
