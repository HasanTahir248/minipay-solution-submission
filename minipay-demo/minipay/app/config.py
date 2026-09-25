import os


class Settings:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "minipay")
    DB_USER = os.getenv("DB_USER", "minipay")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "minipay")

    API_KEY = os.getenv("API_KEY", "demo-api-key")
    SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me-in-prod")

    LOGIN_USER = os.getenv("LOGIN_USER", "admin")
    LOGIN_PASS = os.getenv("LOGIN_PASS", "admin123")


settings = Settings()
