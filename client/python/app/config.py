import os
from dataclasses import dataclass


@dataclass
class Config:
    NAME: str = os.getenv("NAME", "World")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SERVER_HOST: str = os.getenv("SERVER_HOST", "localhost")
    SERVER_PORT: str = os.getenv("SERVER_PORT", "50050")
    SERVER_ADDRESS: str = f"{SERVER_HOST}:{SERVER_PORT}"
    INFINITE: bool = os.getenv("INFINITE", "False").lower() in {"true", "1", "yes"}


config = Config()
