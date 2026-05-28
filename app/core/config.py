from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding='utf-8', extra='ignore')

    APP_NAME: str = 'Whyvo API'
    SECRET_KEY: str = 'change-me'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = 'sqlite:///./whyvo.db'
    OTP_BYPASS_CODE: str = '123456'
    SMTP_HOST: str = ''
    SMTP_PORT: int = 587
    SMTP_USER: str = ''
    SMTP_PASS: str = ''
    SMTP_FROM: str = 'no-reply@whyvo.app'
    TWILIO_ACCOUNT_SID: str = ''
    TWILIO_AUTH_TOKEN: str = ''
    TWILIO_FROM_NUMBER: str = ''
    FIREBASE_PROJECT_ID: str = ''
    FIREBASE_SERVICE_ACCOUNT_JSON: str = ''
    FRONTEND_ORIGINS: str = 'http://127.0.0.1:5173'
    FORCE_HTTPS: bool = False


settings = Settings()
