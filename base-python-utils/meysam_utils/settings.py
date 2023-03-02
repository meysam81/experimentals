from enum import Enum

from pydantic import BaseSettings as _BaseSettings
from pydantic import root_validator


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Scheme(str, Enum):
    HTTP = "http"
    HTTPS = "https"


class BaseSettings(_BaseSettings):
    SCHEME: Scheme = Scheme.HTTP
    HOST: str = "localhost"
    PORT: int | None
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEBUG: bool = True

    @root_validator
    def validate_settings(cls, values):
        if values["DEBUG"]:
            values["LOG_LEVEL"] = LogLevel.DEBUG
        if isinstance(values["LOG_LEVEL"], LogLevel):
            values["LOG_LEVEL"] = values["LOG_LEVEL"].value
        values["SCHEME"] = values["SCHEME"].value
        return values
