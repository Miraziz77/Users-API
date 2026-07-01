from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    PROJECT_NAME: str
    ENVIRONMENT: str

    # Database
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Verification
    VERIFICATION_CODE_EXPIRE_HOURS: int
    UNVERIFIED_USER_TTL_DAYS: int

    # Celery / Redis
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # SMTP (email verification)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_USE_TLS: bool
    EMAIL_FROM: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()