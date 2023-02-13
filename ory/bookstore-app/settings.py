from base_utils import BaseSettings, LogLevel


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 41000
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///../../persistence/bookstore.db"
    ENABLE_FOREIGN_KEYS: bool = True
    WORKERS: int = 1

    KETO_READ_URL: str = "http://localhost:40720"
    KETO_WRITE_URL: str = "http://localhost:40730"

    @property
    def db_extras(self):
        if self.DATABASE_URL.startswith("sqlite"):
            return {"check_same_thread": False}
        return {}

    @property
    def db_session_config(self):
        return {"autocommit": False, "autoflush": False}


config = Settings()
