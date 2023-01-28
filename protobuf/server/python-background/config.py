import os
from dataclasses import dataclass as ds


@ds
class Config:
    BROKER: str = os.getenv("BROKER", "amqp://guest:guest@localhost:5672")


config = Config()
