from enum import Enum

from pydantic import BaseSettings as _BaseSettings
from pydantic import root_validator


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BaseSettings(_BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int
    LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEBUG: bool = True

    @root_validator
    def root_validator_(cls, values):
        if values["DEBUG"]:
            values["LOG_LEVEL"] = LogLevel.DEBUG
        values["LOG_LEVEL"] = values["LOG_LEVEL"].value
        return values
