from base_utils import BaseSettings, LogLevel


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 41000
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEBUG: bool = True


config = Settings()
