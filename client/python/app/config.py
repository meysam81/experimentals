import os
from dataclasses import dataclass


@dataclass
class Config:
    NAME: str = os.getenv("NAME", "World")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SERVER_ADDRESS: str = os.getenv("SERVER_ADDRESS", "localhost:50051")


config = Config()
