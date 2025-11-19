from typing import List


class Settings:
    PROJECT_NAME: str = "AppetIte API"
    API_V1_PREFIX: str = ""

    DATABASE_URL: str = "sqlite:///./appetite_users.db"

    JWT_SECRET_KEY: str = "super-secret-change-me" 
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()