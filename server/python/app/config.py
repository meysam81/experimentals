import os
from dataclasses import dataclass


@dataclass
class Config:
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT: str = os.getenv("PORT", "50051")
    THREAD_POOL: int = os.getenv("THREAD_POOL", 10)


config = Config()
