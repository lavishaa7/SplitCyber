import os

class Settings:
    PROJECT_NAME: str = "SplitCyber - Group Expense Splitter"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # MySQL Database Settings
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "password")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: str = os.getenv("MYSQL_PORT", "3306")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "expense_db")

    # Default MySQL database URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    )

    # SQLite fallback path if MySQL connection is unavailable
    SQLITE_FALLBACK_URL: str = "sqlite:///./expense_db.db"

settings = Settings()
