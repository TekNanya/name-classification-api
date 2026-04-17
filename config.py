import os


class Settings:
    # ---------------- PROJECT ----------------
    PROJECT_NAME: str = "Name Classification API"
    API_VERSION: str = "1.0.0"

    # ---------------- DATABASE ----------------
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db"
    )

    # ---------------- EXTERNAL APIS ----------------
    GENDERIZE_URL: str = "https://api.genderize.io"
    AGIFY_URL: str = "https://api.agify.io"
    NATIONALIZE_URL: str = "https://api.nationalize.io"

    # ---------------- PERFORMANCE ----------------
    REQUEST_TIMEOUT: int = 5


settings = Settings()