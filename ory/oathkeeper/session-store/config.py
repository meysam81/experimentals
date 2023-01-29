import json
from enum import Enum

from pydantic import BaseSettings, root_validator


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    LOG_LEVEL: LogLevel = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 9200
    DEBUG: bool = True

    PUBKEY_PATH: str = "./keys/jwk.pub.json"
    PRIVKEY_PATH: str = "./keys/jwk.json"

    KRATOS_PUBLIC_URL: str = "http://127.0.0.1:4433"

    @root_validator
    def validate_settings(cls, values):
        if values["DEBUG"]:
            values["LOG_LEVEL"] = "DEBUG"
        return values

    @property
    def jwk_pubkey(self):
        with open(self.PUBKEY_PATH, "r") as f:
            return json.load(f)


settings = Settings()
