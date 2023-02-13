from base_utils import BaseSettings, LogLevel


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 41000
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite://../../persistence/bookstore.db"

    @property
    def db_extras(self):
        if self.DATABASE_URL.startswith("sqlite"):
            return {"check_same_thread": False}
        return {}

    @property
    def db_session_config(self):
        return {"autocommit": False, "autoflush": False}


config = Settings()
